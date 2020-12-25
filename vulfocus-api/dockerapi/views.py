import socket
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from dockerapi.models import ImageInfo
from dockerapi.serializers import ImageInfoSerializer, ContainerVulSerializer, SysLogSerializer
from dockerapi.models import ContainerVul
import django.utils
import django.utils.timezone as timezone
from .common import R, DEFAULT_CONFIG, get_setting_config
from django.db.models import Q
from .models import SysLog, SysConfig
import json
from tasks import tasks
from vulfocus.settings import client, VUL_IP
from tasks.models import TaskInfo
import re
from rest_framework.decorators import api_view


def get_request_ip(request):
    """
    获取请求IP
    :param request:
    :return:
    """
    request_ip = ""
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        request_ip = request.META.get("HTTP_X_FORWARDED_FOR")
    else:
        request_ip = request.META.get("REMOTE_ADDR")
    return request_ip


class ImageInfoViewSet(viewsets.ModelViewSet):
    serializer_class = ImageInfoSerializer

    def get_queryset(self):
        query = self.request.GET.get("query", "")
        flag = self.request.GET.get("flag", "")
        user = self.request.user
        if user.is_superuser:
            if query:
                query = query.strip()
                if flag and flag == "flag":
                    image_info_list = ImageInfo.objects.filter(Q(image_name__contains=query) | Q(image_vul_name__contains=query)
                                                       | Q(image_desc__contains=query)).order_by('-create_date')
                else:
                    image_info_list = ImageInfo.objects.filter(Q(image_name__contains=query) | Q(image_vul_name__contains=query)
                                                       | Q(image_desc__contains=query),is_ok=True).order_by('-create_date')
            else:
                if flag and flag == "flag":
                    image_info_list = ImageInfo.objects.filter().order_by('-create_date')
                else:
                    image_info_list = ImageInfo.objects.filter(is_ok=True).order_by('-create_date')
        else:
            if query:
                query = query.strip()
                image_info_list = ImageInfo.objects.filter(Q(image_name__contains=query) | Q(image_vul_name__contains=query)
                                                       | Q(image_desc__contains=query), is_ok=True).order_by('-create_date')
            else:
                image_info_list = ImageInfo.objects.filter(is_ok=True).order_by('-create_date')
        return image_info_list

    def destroy(self, request, *args, **kwargs):
        return JsonResponse(R.ok())

    @action(methods=["post"], detail=True, url_path="edit")
    def edit_image(self, request, pk=None):
        """
        修改镜像
        :param request:
        :param pk:
        :return:
        """
        user = request.user
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足"))
        data = request.data
        image_info = ImageInfo.objects.filter(image_id=pk).first()
        if not image_info:
            return JsonResponse(R.build(msg="镜像不存在"))
        if "rank" in data:
            try:
                rank = float(data["rank"])
            except:
                rank = 2.5
            image_info.rank = rank
        if "image_vul_name" in data:
            image_vul_name = data["image_vul_name"]
            image_vul_name = image_vul_name.strip()
            image_info.image_vul_name = image_vul_name
        if "image_desc" in data:
            image_desc = data["image_desc"]
            image_desc = image_desc.strip()
            image_info.image_desc = image_desc
        image_info.update_date = django.utils.timezone.now()
        image_info.save()
        return JsonResponse(R.ok())

    def update(self, request, *args, **kwargs):
        return JsonResponse(R.ok())

    def create(self, request, *args, **kwargs):
        """
        创建镜像
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user = request.user
        image_name = request.POST.get("image_name", "")
        image_vul_name = request.POST.get("image_vul_name", "")
        image_desc = request.POST.get("image_desc", "")
        try:
            image_rank = request.POST.get("rank", default=2.5)
            image_rank = float(image_rank)
        except:
            image_rank = 2.5
        image_file = request.FILES.get("file")
        image_info = None
        if image_name:
            if ":" not in image_name:
                image_name += ":latest"
            image_info = ImageInfo.objects.filter(image_name=image_name).first()
        if not image_info:
            image_info = ImageInfo(image_name=image_name, image_vul_name=image_vul_name, image_desc=image_desc,
                                   rank=image_rank, is_ok=False, create_date=timezone.now(), update_date=timezone.now())
            if not image_file:
                image_info.save()
        task_id = tasks.create_image_task(image_info=image_info, user_info=user, request_ip=get_request_ip(request),
                                          image_file=image_file)
        if image_file:
            task_info = TaskInfo.objects.filter(task_id=task_id).first()
            task_msg = task_info.task_msg
            return JsonResponse(json.loads(task_msg))
        return JsonResponse(R.ok(task_id, msg="拉取镜像%s任务下发成功" % (image_name, )))

    @action(methods=["get"], detail=True, url_path="download")
    def download_image(self, request, pk=None):
        """
        下载镜像
        :param request:
        :param pk:
        :return:
        """
        user = request.user
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足"))
        image_info = ImageInfo.objects.filter(image_id=pk).first()
        if not image_info:
            return JsonResponse(R.build(msg="镜像不存在"))
        task_id = tasks.create_image_task(image_info=image_info, user_info=user, request_ip=get_request_ip(request))
        return JsonResponse(R.ok(task_id, msg="拉取镜像%s任务下发成功" % (image_info.image_name, )))

    @action(methods=["get"], detail=True, url_path="share")
    def share_image(self, request, pk=None):
        """
        分享镜像
        :param request:
        :param pk:
        :return:
        """
        user = request.user
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足"))
        img_info = ImageInfo.objects.filter(image_id=pk).first()
        if not img_info:
            return JsonResponse(R.build(msg="镜像不存在"))
        setting_config = get_setting_config()
        share_username = setting_config["share_username"]
        share_username = share_username.strip()
        if not share_username:
            return JsonResponse(R.build(msg="分享用户名不能为空，请在系统管理中的系统配置模块进行配置分享用户名。"))
        share_username_reg = "[\da-zA-z\-]+"
        if not re.match(share_username_reg, share_username):
            return JsonResponse(R.build(msg="分享用户名不符合要求"))
        task_id = tasks.share_image_task(image_info=img_info, user_info=user, request_ip=get_request_ip(request))
        return JsonResponse(R.ok(task_id))

    @action(methods=["get"], detail=True, url_path="local")
    def local(self, request, pk=None):
        """
        加载本地镜像
        :param request:
        :param pk:
        :return:
        """
        user = request.user
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足"))
        local_images = client.images.list()
        db_image_list = ImageInfo.objects.filter(is_ok=True)
        db_image_name_list = []
        for db_image in db_image_list:
            db_image_name_list.append(db_image.image_name)
        result_info = []
        for image_info in local_images:
            for image_tag in image_info.tags:
                tmp_info = {"name": image_tag, "flag": False}
                if image_tag in db_image_name_list:
                    tmp_info["flag"] = True
                result_info.append(tmp_info)
        return JsonResponse(R.ok(result_info))

    @action(methods=["post"], detail=True, url_path="local_add")
    def batch_local_add(self, request, pk=None):
        """
        批量添加本地镜像
        :param request:
        :param pk:
        :return:
        """
        user = request.user
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足"))
        image_name_str = request.POST.get("image_names", "")
        image_names = image_name_str.split(",")
        rsp_msg = []
        for image_name in image_names:
            if not image_name:
                continue
            if ":" not in image_name:
                image_name += ":latest"
            image_info = ImageInfo.objects.filter(image_name=image_name).first()
            if not image_info:
                image_vul_name = image_name[:image_name.rfind(":")]
                image_info = ImageInfo(image_name=image_name, image_vul_name=image_vul_name, image_desc=image_vul_name,
                                       rank=2.5, is_ok=False, create_date=timezone.now(), update_date=timezone.now())
                image_info.save()
            task_id = tasks.create_image_task(image_info=image_info, user_info=user, request_ip=get_request_ip(request),
                                              image_file=None)
            if task_id:
                rsp_msg.append("拉取镜像%s任务下发成功" % (image_name,))
        return JsonResponse(R.ok(data=rsp_msg))

    @action(methods=["get"], detail=True, url_path="delete")
    def delete_image(self, request, pk=None):
        """
        删除镜像
        :param request:
        :param pk:
        :return:
        """
        user = request.user
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足"))
        img_info = ImageInfo.objects.filter(image_id=pk).first()
        if not img_info:
            return JsonResponse(R.ok())
        operation_args = ImageInfoSerializer(img_info).data
        request_ip = get_request_ip(request)
        sys_log = SysLog(user_id=user.id, operation_type="镜像", operation_name="删除",
                         operation_value=operation_args["image_vul_name"], operation_args=json.dumps(operation_args), ip=request_ip)
        sys_log.save()
        image_id = img_info.image_id
        container_vul = ContainerVul.objects.filter(image_id=image_id)
        data_json = ContainerVulSerializer(container_vul, many=True)
        if container_vul.count() == 0:
            img_info.delete()
            return JsonResponse(R.ok())
        else:
            return JsonResponse(R.build(msg="镜像正在使用，无法删除！", data=data_json.data))

    @action(methods=["post", "get"], detail=True, url_path="start")
    def start_container(self, request, pk=None):
        """
        启动镜像
        :param request:
        :param pk:
        :return:
        """
        img_info = self.get_object()
        # 当前用户登录ID
        user = request.user
        image_id = img_info.image_id
        user_id = user.id
        container_vul = ContainerVul.objects.filter(user_id=user_id, image_id=image_id, time_model_id="").first()
        if not container_vul:
            container_vul = ContainerVul(image_id=img_info, user_id=user_id, vul_host="", container_status="stop",
                                         docker_container_id="",
                                         vul_port="",
                                         container_port="",
                                         time_model_id="",
                                         create_date=django.utils.timezone.now(),
                                         container_flag="")
            container_vul.save()
        task_id = tasks.create_container_task(container_vul, user, get_request_ip(request))
        return JsonResponse(R.ok(task_id))


class ContainerVulViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = ContainerVulSerializer

    def get_queryset(self):
        request = self.request
        user = request.user
        flag = request.GET.get("flag", "")
        image_id = request.GET.get("image_id", "")
        if flag == 'list' and user.is_superuser:
            if image_id:
                container_vul_list = ContainerVul.objects.filter(image_id=image_id).order_by('-create_date')
            else:
                container_vul_list = ContainerVul.objects.all().order_by('-create_date')
        else:
            container_vul_list = ContainerVul.objects.filter(user_id=self.request.user.id, time_model_id="")
        return container_vul_list

    @action(methods=["get"], detail=True, url_path='start')
    def start_container(self, request, pk=None):
        """
        启动容器
        :param request:
        :param pk:
        :return:
        """
        user_info = request.user
        container_vul = self.get_object()
        task_id = tasks.create_container_task(container_vul=container_vul, user_info=user_info,
                                              request_ip=get_request_ip(request))
        return JsonResponse(R.ok(task_id))

    @action(methods=["get"], detail=True, url_path='stop')
    def stop_container(self, request, pk=None):
        """
        停止容器运行
        :param request:
        :param pk:
        :return:
        """
        user_info = request.user
        container_vul = self.get_object()
        task_id = tasks.stop_container_task(container_vul=container_vul, user_info=user_info,
                                            request_ip=get_request_ip(request))
        return JsonResponse(R.ok(task_id))

    @action(methods=["delete"], detail=True, url_path="delete")
    def delete_container(self, request, pk=None):
        """
        删除容器
        :param request:
        :param pk:
        :return:
        """
        if not pk:
            return JsonResponse(R.build(msg="id不能为空"))
        container_vul = ContainerVul.objects.filter(Q(docker_container_id__isnull=False), ~Q(docker_container_id=''),
                                                    container_id=pk).first()
        if not container_vul:
            return JsonResponse(R.build(msg="环境不存在"))
        user_info = request.user
        # container_vul = self.get_object()
        task_id = tasks.delete_container_task(container_vul=container_vul, user_info=user_info,
                                              request_ip=get_request_ip(request))
        return JsonResponse(R.ok(task_id))

    @action(methods=["post", "get"], detail=True, url_path="flag")
    def check_flag(self, request, pk=None):
        """
        验证Flag是否正确
        :param request:
        :param pk:
        :return:
        """
        flag = request.GET.get('flag', None)
        container_vul = self.get_object()
        user_info = request.user
        user_id = user_info.id
        operation_args = ContainerVulSerializer(container_vul).data
        request_ip = get_request_ip(request)
        sys_log = SysLog(user_id=user_id, operation_type="容器", operation_name="提交Flag",
                         operation_value=operation_args["vul_name"], operation_args={"flag": flag},
                         ip=request_ip)
        sys_log.save()

        if user_id != container_vul.user_id:
            return JsonResponse(R.build(msg="Flag 与用户不匹配"))
        if not flag:
            return JsonResponse(R.build(msg="Flag不能为空"))
        if flag != container_vul.container_flag:
            return JsonResponse(R.build(msg="flag错误"))
        else:
            if not container_vul.is_check:
                # 更新为通过
                container_vul.is_check_date = timezone.now()
                container_vul.is_check = True
                container_vul.save()
                # 停止 Docker
                tasks.stop_container_task(container_vul=container_vul, user_info=user_info,
                                          request_ip=get_request_ip(request))
            return JsonResponse(R.ok())


class SysLogSet(viewsets.ModelViewSet):

    serializer_class = SysLogSerializer

    def get_queryset(self):
        request = self.request
        user = request.user
        if user.is_superuser:
            return SysLog.objects.all().order_by('-create_date')
        else:
            return []


@api_view(http_method_names=["GET"])
def get_setting(request):
    """
    获取配置信息
    :param request:
    :return:
    """
    user = request.user
    if not user.is_superuser:
        return JsonResponse(R.build(msg="权限不足"))
    rsp_data = get_setting_config()
    return JsonResponse(R.ok(data=rsp_data))


@api_view(http_method_names=["POST"])
def update_setting(request):
    """
    更新配置
    :param request:
    :return:
    """
    user = request.user
    if not user.is_superuser:
        return JsonResponse(R.build(msg="权限不足"))
    username = request.POST.get("username", DEFAULT_CONFIG["username"])
    pwd = request.POST.get("pwd", DEFAULT_CONFIG["pwd"])
    time = request.POST.get("time", DEFAULT_CONFIG["time"])
    share_username = request.POST.get("share_username", DEFAULT_CONFIG["share_username"])
    msg_list = []
    build_msg = []
    try:
        time = int(time)
        if time != 0 and time < 60:
            time = int(DEFAULT_CONFIG["time"])
            # msg = "过期时间修改为默认值 30 分钟成功"
            # msg_list.append("过期时间修改为默认值 30 分钟成功")
    except:
        time = int(DEFAULT_CONFIG["time"])
    share_username_config = SysConfig.objects.filter(config_key="share_username").first()
    if not share_username_config:
        username_config = SysConfig(config_key="username", config_value=DEFAULT_CONFIG["username"])
        username_config.save()
    else:
        share_username_reg = "[\da-zA-z\-]+"
        if not share_username:
            build_msg.append("分享用户名不能为空")
        elif not re.match(share_username_reg, share_username):
            build_msg.append("分享用户名不符合要求")
        elif share_username_config.config_value != share_username:
            share_username_config.config_value = share_username
            share_username_config.save()
            msg_list.append("分享用户名修改成功")
    username_config = SysConfig.objects.filter(config_key="username").first()
    if not username_config:
        username_config = SysConfig(config_key="username", config_value=DEFAULT_CONFIG["username"])
        username_config.save()
    else:
        if username_config.config_value != username:
            username_config.config_value = username
            username_config.save()
            msg_list.append("Dockerhub 用户名修改成功")
    pwd_config = SysConfig.objects.filter(config_key="pwd").first()
    if not pwd_config:
        pwd_config = SysConfig(config_key="pwd", config_value=DEFAULT_CONFIG["pwd"])
        pwd_config.save()
    else:
        if pwd_config.config_value != pwd:
            pwd_config.config_value = pwd
            pwd_config.save()
            msg_list.append("Dockerhub Token 修改成功")

    time_config = SysConfig.objects.filter(config_key="time").first()
    if not time_config:
        time_config = SysConfig(config_key="time", config_value=DEFAULT_CONFIG["time"])
        time_config.save()
    else:
        if time_config.config_value != str(time):
            time_config.config_value = str(time)
            time_config.save()
            msg_list.append("镜像过期时间修改成功")

    rsp_data = get_setting_config()
    if len(build_msg) == 0 and len(msg_list) > 0:
        return JsonResponse(R.ok(msg=msg_list, data=rsp_data))
    else:
        build_msg.extend(msg_list)
        return JsonResponse(R.build(msg=build_msg, data=rsp_data))


def get_local_ip():
    """
    获取本机IP
    :return:
    """
    local_ip = ""
    if VUL_IP:
        return VUL_IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()
    return local_ip

