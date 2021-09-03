from django.core.paginator import Paginator
from django.db.models import Sum
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse,HttpResponse
from rest_framework import viewsets,mixins
from user.serializers import UserProfileSerializer, User, UserRegisterSerializer,UpdatePassSerializer,LoginSerializer
from user.serializers import SendEmailSerializer,ResetPasswordSerializer
from rest_framework.views import APIView
from django.contrib.auth import logout, login, authenticate
from user.permissions import IsOwner
from django.db.models import Q
from email.header import Header
from rest_framework.decorators import action
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.views.generic.base import View
from user.models import UserProfile, EmailCode,  RegisterCode
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from rest_framework import permissions, status
from vulfocus.settings import EMAIL_FROM, EMAIL_HOST, EMAIL_HOST_USER
from dockerapi.common import R
from dockerapi.models import ContainerVul
from vulfocus.settings import REDIS_IMG as r_img
from PIL import ImageDraw,ImageFont,Image
import random
import io
import datetime
from user.utils import generate_code, validate_email
import smtplib
import os
from email.mime.text import MIMEText
from time import sleep
import uuid
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.utils import jwt_response_payload_handler
from rest_framework.response import Response
from datetime import datetime, timedelta
from rest_framework_jwt.settings import api_settings
from rest_framework.views import View
from dockerapi.views import get_local_ip
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from vulfocus.settings import REDIS_USER_CACHE as red_user_cache
from vulfocus.settings import ALLOWED_IMG_SUFFIX, BASE_DIR
from dockerapi.views import get_local_ip, get_request_ip
from vulfocus.settings import EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

class ListAndUpdateViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    A viewset that provides default `update()`, `list()`actions.
    """
    pass


class UserSet(ListAndUpdateViewSet):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            user_info = UserProfile.objects.all()
            query = self.request.GET.get('query', '')
            if query:
                user_info = UserProfile.objects.filter(Q(username__contains=query) | Q(email__contains=query)).all()
            return user_info

    def update(self, request, *args, **kwargs):
            user = request.user
            if not user.is_superuser:
                return JsonResponse(R.build(msg="权限不足"))
            new_pwd = request.data.get("pwd", "")
            new_pwd = new_pwd.strip()
            if len(new_pwd) < 6:
                return JsonResponse(R.build(msg="密码格式不正确"))
            user_info = self.get_object()
            user_info.set_password(new_pwd)
            user_info.save()
            return JsonResponse(R.ok())


class get_user_rank(APIView):

    def get(self, request):
        page_no = int(request.GET.get("page", 1))
        score_list = ContainerVul.objects.filter(is_check=True, time_model_id='').values('image_id').distinct().values('user_id').annotate(
            score=Sum("image_id__rank")).values('user_id', 'score').order_by("-score")
        try:
            pages = Paginator(score_list, 20)
            page = pages.page(page_no)
        except Exception as e:
            return JsonResponse(R.err())
        result = []
        for _data in list(page):
            user_info = UserProfile.objects.filter(id=_data["user_id"]).first()
            username = ""
            pass_container_vuls = ""
            user_avatar = ""
            if user_info:
                username = user_info.username
                user_avatar = user_info.avatar
                pass_container_vuls = ContainerVul.objects.filter(is_check=True, user_id=user_info.id, time_model_id='').values('image_id').distinct().count()
            result.append({"rank": _data["score"], "name": username, "image_url": user_avatar, "pass_container_count": pass_container_vuls})

        data = {
            'results': result,
            'count': len(score_list)
        }
        return JsonResponse(R.ok(data=data))


class get_user_info(APIView):
    def get(self, request):
        user_info = User.objects.get(pk=request.user.id)
        serializer = UserProfileSerializer(user_info)
        return JsonResponse(serializer.data)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return JsonResponse({"msg": "OK"})


class UserRegView(viewsets.mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = []
    permission_classes = []
    queryset = UserProfile.objects.all()
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        checkpass = request.data.get("checkpass", "")
        email = request.data.get("email", "")
        captcha_code = request.data.get("captcha_code", "")
        hashkey = request.data.get("hashkey", "")
        if not username:
            return JsonResponse({"code": 400, "msg": "用户名不能为空"})
        if UserProfile.objects.filter(username=username).count():
            return JsonResponse({"code": 400, "msg": "该用户已被注册"})
        if not email:
            return JsonResponse({"code": 400, "msg": "邮箱不能为空"})
        if UserProfile.objects.filter(email=email, has_active=True).count():
            return JsonResponse({"code": 400, "msg": "该邮箱已被注册"})
        if not captcha_code:
            return JsonResponse({"code": 400, "msg": "验证码不能为空"})
        if not judge_captcha(captcha_code, hashkey):
            return JsonResponse({"code": 400, "msg": "验证码错误"})
        if password != checkpass:
            return JsonResponse({"code": 400, "msg": "两次密码输入不一致"})
        code = generate_code(6)
        keys = red_user_cache.keys()
        for single_key in keys:
            try:
                single_user_info = red_user_cache.get(single_key)
                redis_username, redis_password, redis_email = single_user_info.split("-")
                if username == redis_username:
                    return JsonResponse({"code": 400, "msg": "该用户已被注册"})
                if redis_email == email:
                    return JsonResponse({"code": 400, "msg": "该邮箱已被注册"})
            except Exception as e:
                return JsonResponse({"code": 400, "msg": "用户注册失败"})
        try:
            send_activate_email(receiver_email=email, code=code, request=request)
        except smtplib.SMTPDataError as e:
            return JsonResponse({"code": 400, "msg": "邮件发送失败，请减缓发送频率"})
        red_user_cache.set(code, username + "-" + password + "-" + email, ex=300)
        return JsonResponse({"code": 200, "msg": "注册成功"})

# 定义一验证码
class MyCode(View):

    # 定义一个随机验证颜色
    def get_random_color(self):
        R = random.randrange(255)
        G = random.randrange(255)
        B = random.randrange(255)
        return (R,G,B)
    # 随机验证码
    def get(self,request):
        img_size = (110,50)
        image = Image.new('RGB',img_size,'#27408B')
        draw = ImageDraw.Draw(image,'RGB')
        source = '0123456789abcdefghijklmnopqrstevwxyz'
        code_str = ''
        for i in range(4):
            text_color = self.get_random_color()
            tmp_num = random.randrange(len(source))
            random_str = source[tmp_num]
            code_str +=random_str
            draw.text((10+30*i,20),random_str,text_color,)
        buf = io.BytesIO()
        image.save(buf, 'png')
        data = buf.getvalue()
        if "HTTP_X_REAL_IP" in request.META:
            ip = request.META.get("HTTP_X_REAL_IP")
        else:
            ip = request.META.get("REMOTE_ADDR")
        if ip == "127.0.0.1":
            return HttpResponse(data, 'image/png')
        r_img.sadd(ip, code_str)
        r_img.expire(ip, 60)
        return HttpResponse(data, 'image/png')


class UpdatePassViewset(mixins.UpdateModelMixin,viewsets.GenericViewSet):
    serializer_class = UpdatePassSerializer
    permission_classes = [permissions.IsAuthenticated,IsOwner]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):

        oldPassword = request.data['oldPassword'].strip()
        password = request.data["pass"].strip()
        checkPassword = request.data["checkPass"].strip()
        if not oldPassword:
            return JsonResponse({"code": 401, "msg": "旧密码不能为空"})
        if len(checkPassword) < 8:
            return JsonResponse({"code": 401, "msg": "密码不得少于8位"})
        if password != checkPassword:
            return JsonResponse({"code": 401, "msg": "两次密码不一致"})
        user = self.request.user
        if not user.check_password(oldPassword):
            return JsonResponse({"code": 401, "msg": "旧密码错误"})
        user.set_password(raw_password=checkPassword)
        user.save()
        return JsonResponse({"code": 200, "msg": "修改密码成功"})


#自定义登录
class LoginViewset(mixins.CreateModelMixin,viewsets.GenericViewSet):
    serializer_class = LoginSerializer
    queryset = User.objects.all()
    permission_classes = []
    authentication_classes = ()
    def create(self, request, *args, **kwargs):
        username = request.data["username"]
        password = request.data["password"]
        keys = red_user_cache.keys()
        for single_key in keys:
            user_info = red_user_cache.get(single_key)
            redis_username, redis_password, redis_email = user_info.split("-")
            if redis_username == username:
                return Response({"non_field_errors": ["账号未激活，请先激活账号"]}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(username=username).first()
        if not user:
            return Response({"non_field_errors": ["账号或者密码错误"]}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            return Response({"non_field_errors": ["账号或者密码错误"]}, status=status.HTTP_400_BAD_REQUEST)
        if not user.has_active:
            return Response({"non_field_errors": ["账号未激活，请先激活账号"]}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #采用jwt模式认证
        serializer_instance = JSONWebTokenSerializer(data=request.data)
        if serializer_instance.is_valid():
            user = serializer_instance.object.get('user') or request.user
            token = serializer_instance.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class SendEmailViewset(mixins.CreateModelMixin,viewsets.GenericViewSet):
    serializer_class = SendEmailSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        http_referer = request.META.get('HTTP_REFERER')
        serializer = self.get_serializer(data=request.data)
        username = request.data.get("username", None)
        hashkey = request.data.get("hashkey", "")
        captcha_code = request.data.get("captcha_code", "")
        if not hashkey:
            return JsonResponse({"code": 400, "msg": "验证码哈希值不能为空"})
        if not captcha_code:
            return JsonResponse({"code": 400, "msg": "验证码不能为空"})
        if not judge_captcha(captcha_code, hashkey):
            return JsonResponse({"code": 400, "msg": "验证码输入错误"})
        if not User.objects.filter(username=username).count():
            return JsonResponse({"code": 400, "msg": "该用户不存在"})
        user = User.objects.get(username=username)
        one_minute_ago = datetime.now()-timedelta(minutes=1)
        if EmailCode.objects.filter(user=user, add_time__gt=one_minute_ago).count():
            return JsonResponse({"code": 400, "msg": "距离上次发送未超过一分钟"})
        code = generate_code()
        #判断数据库中是否有相同的验证码记录
        while EmailCode.objects.filter(code=code).count():
            code = generate_code()
        email_instance = EmailCode(user=user, code=code, email=user.email)
        try:
            send_mail(subject="找回密码", message="{http_referer}#/updatepwd?code={code}。有效期为5分钟".format(http_referer=http_referer, code=code), from_email=EMAIL_FROM,
                          recipient_list=[user.email])
        except:
            return JsonResponse({"code": 400, "msg": "邮件发送失败"})
        email_instance.save()
        return JsonResponse({"code": 200, "msg": "ok"})



#重置密码
class ResetPasswordViewset(mixins.UpdateModelMixin,viewsets.GenericViewSet):
    serializer_class = ResetPasswordSerializer
    permission_classes = []


    def update(self, request, *args, **kwargs):
        code = request.data.get("code", "")
        password = request.data.get("pass", "")
        check_password = request.data.get("checkPass", "")
        if not code:
            return JsonResponse({"code": 400, "msg": "错误的请求"})
        five_minutes_ago = datetime.now() - timedelta(minutes=5)
        email_instance = EmailCode.objects.filter(code=code).first()
        if not email_instance:
            return JsonResponse({"code": 400, "msg": "链接失效"})
        if email_instance.add_time <= five_minutes_ago:
            return JsonResponse({"code": 400, "msg": "验证码已过期"})
        password = request.data['pass']
        if not password or not check_password:
            return JsonResponse({"code": 400, "msg": "密码不能为空"})
        if len(password) < 8:
            return JsonResponse({"code": 400, "msg": "密码长度不能小于8位"})
        if password != check_password:
            return JsonResponse({"code": 400, "msg": "两次输入密码不一致"})
        user = email_instance.user
        user.set_password(password)
        user.save()
        email_instances = EmailCode.objects.filter(code=code).all()
        for email_i in email_instances:
            email_i.delete()
        return JsonResponse({"code": 200, "msg": "密码找回成功"})


class AccessLinkView(View):
    def get(self,request):
        '''
        验证链接是否有效
        '''
        code=request.GET.get("code","")
        try:
            user_info = red_user_cache.get(code)
            redis_username, redis_password, redis_email = user_info.split("-")
            user = UserProfile(username=redis_username, email=redis_email)
            user.set_password(redis_password)
            user.has_active = True
            user.greenhand = True
            user.save()
            red_user_cache.delete(code)
        except Exception as e:
            return JsonResponse({"code": 400, "msg": "链接不存在或已失效"})
        return JsonResponse({"code": 200, "msg": "ok"})

@api_view(http_method_names=["POST"])
@authentication_classes([])
@permission_classes([])
def send_register_email(request):
    email = request.POST.get("email", "")
    code = generate_code(6)
    if not email:
        return JsonResponse({"code": 400, "msg": "邮箱不能为空"})
    if UserProfile.objects.filter(email=email).count():
        return JsonResponse({"code": 400, "msg": "该邮箱已经被使用"})
    if RegisterCode.objects.filter(email=email, add_time__gt=datetime.now()-timedelta(minutes=1)).count():
        return JsonResponse({"code": 400, "msg": "距离上次发送未超过1分钟"})
    try:
        send_mail(subject="用户注册", from_email=EMAIL_FROM, message="您的验证码是{}，有效期为三分钟".format(code),
                  recipient_list=[email])
        register_code = RegisterCode(email=email, code=code)
        register_code.save()
        return JsonResponse({"code": 200, "msg": "邮件发送成功"})
    except Exception as e:
        return JsonResponse({"code": 400, "msg": "邮件发送失败"})


# 生成验证码
def captcha():
    hashkey = CaptchaStore.generate_key()
    image_url = captcha_image_url(hashkey)
    captcha_code = {"hashkey": hashkey, "image_url": image_url}
    return captcha_code


# 判断验证码是否有效
def judge_captcha(captchastr, captchahashkey):
    if captchastr and captchahashkey:
        try:
            captcha_instance = CaptchaStore.objects.get(hashkey=captchahashkey)
            if captcha_instance.challenge == captchastr.upper():
                captcha_instance.delete()
                return True
        except Exception as e:
            return False
    else:
        return False


# 刷新验证码
@api_view(http_method_names=["GET"])
@authentication_classes([])
@permission_classes([])
def refresh_captcha(request):
    return JsonResponse(captcha())

def send_activate_email(receiver_email, code, request):
    subject, from_email, to = "用户注册", EMAIL_FROM, receiver_email
    http_referer = request.META.get('HTTP_REFERER')
    msg = EmailMultiAlternatives(subject, '', from_email, [to])
    html_content ="""<div><table cellpadding="0" align="center" width="600" style="background:#fff;width:600px;margin:0 auto;text-align:left;position:relative;font-size:14px; font-family:'lucida Grande',Verdana;line-height:1.5;box-shadow:0 0 5px #999999;border-collapse:collapse;">
    <tbody><tr><th valign="middle" style="height:12px;color:#fff; font-size:14px;font-weight:bold;text-align:left;border-bottom:1px solid #467ec3;background:#2196f3;">
    </th></tr><tr><td><div style="padding:30px  40px;"><img style="float:left;" src="http://www.baimaohui.net/home/image/icon-anquan-logo.png?imageView2">
    <br><br><br><br><h2 style="font-weight:bold; font-size:14px;margin:5px 0;font-family:PingFang-SC-Regular">您好：</h2>
    <p style="color:#31424e;line-height:28px;font-size:14px;margin:20px 0;text-indent:2em;">您正在注册vulfocus，请在5分钟之内点击下方的按钮激活您的账号。</p>
    <a href="{http_referer}#/activate?code={code}" style="color: #e21c23;text-decoration: underline;text-decoration: none;">
    <div style="height: 36px;line-height:36px;width:160px;border-radius:2px;margin:0 auto;margin-top: 30px;font-size: 16px;background:#2196f3;text-align: center;color: #FFF;">激活账户</div></a>
    <p style="color:#31424e;line-height:28px;font-size:14px;margin:20px 0;text-indent:2em;">如果上方按钮不起作用，请复制到您的浏览器中打开。</p>
    <p style="color:#2196f3;line-height:28px;font-size:14px;margin:20px 0;text-indent:2em;">{http_referer}#/activate?code={code}</p>
    </div><div style="background: #f1f1f1;padding: 30px 40px;"><p style="color:#798d99; font-size:12px;padding: 0;margin: 0;">
    Vulfocus 漏洞平台：<a href="http://vulfocus.fofa.so/#/" target="_blank" style="color:#999;text-decoration: none;">http://vulfocus.fofa.so/#/</a><br>
    <span style="background:#ddd;height:1px;width:100%;overflow:hidden;display:block;margin:8px 0;"></span>
    Vulfocus 是一个漏洞集成平台，将漏洞环境 docker 镜像，放入即可使用，开箱即用。<br></p><div class="cons_list" style="text-align: center; margin: 48px 0;">
    <a href="http://vulfocus.fofa.so/#/" style="text-decoration: none;"><img src="http://www.baimaohui.net/home/image/icon-anquan-logo.png" style="width:42px; height:42px; display: inline-block;">
    <p style="width:100%;text-align: center;margin: 20px 0 0 0;"><a href="http://vulfocus.fofa.so/#/" style="border-right: 1px solid #ccc;  font-size:14px;margin: 0; font-weight:500; color:rgba(180,189,194,1); padding: 0 10px;text-decoration: none;">vulfocus首页</a>
    </p></div></div></td></tr></tbody></table>
    </div>""" .format(http_referer=http_referer, code=code)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


class AccessUpdataLinkView(View):
    def get(self,request):
        '''
        验证链接是否有效
        '''
        code=request.GET.get("code","")
        if not EmailCode.objects.filter(code=code).count():
            return JsonResponse({"code": 400, "msg": "该链接不存在或失效"})
        email_instance = EmailCode.objects.get(code=code)
        user = email_instance.user
        five_minutes_ago = datetime.now() - timedelta(minutes=5)
        if email_instance.add_time <= five_minutes_ago:
            return JsonResponse({"code": 400, "msg": "链接已过期"})
        return JsonResponse({"code": 200, "msg": "ok"})


@api_view(http_method_names=["POST"])
def upload_user_img(request):
    user = request.user
    img = request.data.get("img")
    if not img:
        return JsonResponse({"code": 400, "msg": "请上传图片"})
    img_name = img.name
    img_suffix = img_name.split(".")[-1]
    if img_suffix not in ALLOWED_IMG_SUFFIX:
        return JsonResponse({"code": 400, "msg": "不支持此格式图片，请上传%s格式图片" % ("、".join(ALLOWED_IMG_SUFFIX))})
    img_name = str(uuid.uuid4()).replace("-", "")+"."+img_suffix
    static_path = os.path.join(BASE_DIR, "static", "user")
    if not os.path.exists(static_path):
        os.mkdir(static_path)
    #  判断用户是否更新过头像
    if user.avatar != "http://www.baimaohui.net/home/image/icon-anquan-logo.png":
        origin_img_path = user.avatar.split("user")[-1]
        os.remove(static_path+origin_img_path)
    with open(os.path.join(static_path, img_name), "wb") as f:
        for chunk in img.chunks():
            f.write(chunk)
    user.avatar = '/images/user/' + img_name
    user.save()
    return JsonResponse({"code": 200, "msg": "上传成功", "image_path": img_name})
