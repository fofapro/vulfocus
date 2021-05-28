import socket
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from dockerapi.models import ImageInfo
from dockerapi.serializers import ImageInfoSerializer, ContainerVulSerializer, SysLogSerializer, TimeMoudelSerializer, TimeRankSerializer, TimeTempSerializer
from dockerapi.models import ContainerVul
from user.serializers import UserProfileSerializer
from user.models import UserProfile
import django.utils
import django.utils.timezone as timezone
from .common import R, DEFAULT_CONFIG, get_setting_config
from django.db.models import Q
from .models import SysLog, SysConfig, TimeMoudel, TimeTemp, TimeRank
import json
from tasks import tasks
from vulfocus.settings import client, VUL_IP
from tasks.models import TaskInfo
import re
from rest_framework.decorators import api_view
import time
import datetime
import uuid

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

class CreateTimeTemplate(viewsets.ModelViewSet):

    serializer_class = TimeTempSerializer

    def get_queryset(self, *args, **kwargs):

        request = self.request
        r_ip = get_request_ip(request)
        user_id = request.user.id
        now_time = datetime.datetime.now().timestamp()
        return TimeTemp.objects.all()


    # 创建计时模式模版
    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        time_desc = request.data['desc']
        if request.data['time_range'].isdigit() != True or int(request.data['time_range']) % 30 != 0:
            data = {
                "code": 2001,
                "message": "时间范围必须是整数，并且是30的倍数",
            }
            return JsonResponse(data=data)
        time_data = TimeTemp.objects.filter(time_range=int(request.data['time_range'])).first()
        if time_data:
            data = {
                "code": 2001,
                "message": "该时间模式已经创建",
            }
            return JsonResponse(data=data)
        try:
            time_range = request.data['time_range']
        except Exception as e:
            return JsonResponse(data={"code": 2001, "message": "时间范围不能为空"})
        img = request.data['imageName']
        timetemp_info = TimeTemp(user_id=user_id, time_range=int(time_range), time_desc=time_desc, image_name=img)
        timetemp_info.save()
        data = self.serializer_class(timetemp_info).data
        return JsonResponse(R.ok(data=data))

    def destroy(self, request, *args, **kwargs):
        user = request.user
        now_time = datetime.datetime.now().timestamp()
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足"))
        request = self.request

        if "id" in request.data:
            temp_id = request.data['id']
        else:
            temp = self.get_object()
            temp_id = self.get_serializer(temp).data['temp_id']
        data = TimeMoudel.objects.filter(temp_time_id_id=temp_id,end_time__gte=now_time).first()
        if data:
            return JsonResponse({"code": 2001, "message": "删除失败，该模版计时模式已启动"})
        try:
            temp = TimeTemp.objects.filter(temp_id=temp_id).first()
            temp.delete()
        except Exception as e:
            return JsonResponse({"code": 2001, "message": "删除失败"})
        return JsonResponse({"code": 200, "message": "删除成功"})


class TimeRankSet(viewsets.ModelViewSet):
    serializer_class = TimeRankSerializer

    def get_queryset(self):
        value = self.request.GET.get("value")
        time_data = TimeTemp.objects.all().filter(time_range=value).first()
        temp_data = TimeRank.objects.all().filter(time_temp_id=time_data.temp_id)
        return temp_data




class TimeMoudelSet(viewsets.ModelViewSet):

    serializer_class = TimeMoudelSerializer

    def get_queryset(self):
        data = TimeMoudel.objects.all().filter(user_id=self.request.user.id, status=True)
        return data

    '''
    删除时间模式，删除会所有该用户目前运行的容器
    '''
    def delete(self, request, *args, **kwargs):
        user_id = request.user.id
        now_time = datetime.datetime.now().timestamp()
        try:
            auto_end_data = TimeMoudel.objects.filter(user_id=user_id, end_time__lte=now_time).first()
            if auto_end_data:
                time_id = auto_end_data.time_id
                container_vul_list = ContainerVul.objects.filter(user_id=user_id, time_model_id=time_id)
                TimeMoudel.objects.filter(user_id=user_id, end_time__lte=now_time).delete()
            else:
                data = TimeMoudel.objects.filter(user_id=user_id, end_time__gte=now_time).first()
                time_id = data.time_id
                TimeMoudel.objects.filter(user_id=user_id, end_time__gte=now_time).delete()
                container_vul_list = ContainerVul.objects.filter(user_id=user_id, time_model_id=time_id)
            for container_vul in container_vul_list:
                try:
                    docker_container_id = container_vul.docker_container_id
                    # 移除Docker容器
                    docker_container = client.containers.get(container_id=docker_container_id)
                    docker_container.remove()
                except Exception as e:
                    pass
                container_vul.delete()
            return JsonResponse({"code": "2000", "msg": "成功"}, status=201)
        except Exception as e:
            print(e)
            return JsonResponse({"code": "2001", "msg": str(e)})

    '''
    获取时间模式数据信息
    '''
    @action(methods=['get'], detail=False, url_path="info")
    def info(self, request, pk=None):
        user_id = request.user.id
        now_time = datetime.datetime.now().timestamp()
        user_data = UserProfile.objects.filter(id=user_id).first()
        data = TimeMoudel.objects.filter(user_id=user_id, end_time__gte=now_time).first()
        if not data:
            return JsonResponse({"code": "2001", "msg": "不在答题模式中", "data": ""})
        time_moudel_serializer = TimeMoudelSerializer(data)
        info = time_moudel_serializer.data
        # 计算分数
        time_id = data.time_id
        total_rank = 0.0
        time_moudel_vul_list = ContainerVul.objects.filter(time_model_id=time_id,is_check=True)
        for time_moudel_vul in time_moudel_vul_list:
            total_rank += time_moudel_vul.image_id.rank
        trdata = TimeRank.objects.filter(time_temp_id=data.temp_time_id_id,user_id=user_id).first()
        if trdata:
            trdata.update(rank=total_rank)
        else:
            tr = TimeRank(user_id=user_id, rank=total_rank, time_temp_id=data.temp_time_id_id,
                          user_name=user_data.username)
            tr.save()
        info['rank'] = total_rank
        return JsonResponse({"code": "200", "msg": "", "data": info})

    '''
    检测是否时间过期
    '''
    @action(methods=['get'], detail=False, url_path="check")
    def check(self, request, pk=None):
        user_id = request.user.id
        now_time = datetime.datetime.now().timestamp()
        data = TimeMoudel.objects.filter(user_id=user_id, end_time__gte=now_time).first()
        if data:
            # 移除所有的镜像
            container_vul_list = ContainerVul.objects.filter(user_id=user_id)
            for container_vul in container_vul_list:
                try:
                    docker_container_id = container_vul.docker_container_id
                    # 移除Docker
                    docker_container = client.containers.get(container_id=docker_container_id)
                    docker_container.remove()
                except Exception as e:
                    pass
                container_vul.delete()
            return JsonResponse({"code": "200", "msg": "OK"})
        else:
            return JsonResponse({"code": "2001", "msg": "时间已到"})

    '''
    创建计分模式
    '''

    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        now_time = datetime.datetime.now().timestamp()
        time_minute = request.data['time_range']
        temp_id = request.data['temp_id']
        data = TimeMoudel.objects.filter(user_id=user_id, end_time__gte=now_time).first()
        rankdata = TimeRank.objects.filter(user_id=user_id,time_temp_id=temp_id).first()
        user_data = UserProfile.objects.filter(id=user_id).first()
        if not rankdata:
            rd = TimeRank(rank_id=str(uuid.uuid4()), user_id=user_id, user_name=user_data.username, rank=0, time_temp_id=temp_id)
            rd.save()
        if data:
            return JsonResponse({"code": "2001", "msg": "时间未到", "data": ""})
        else:
            try:
                request_ip = get_request_ip(request)
                sys_log = SysLog(user_id=user_id, operation_type="时间模式", operation_name="创建 ", operation_value="",
                                 operation_args={},
                                 ip=request_ip)
                sys_log.save()
            except Exception as e:
                pass
            now_time = datetime.datetime.now()
            end_time = now_time + datetime.timedelta(minutes=time_minute)
            start_time_timestamp = now_time.timestamp()
            end_time_timestamp = end_time.timestamp()
            time_moudel = TimeMoudel(time_id=str(uuid.uuid4()), user_id=user_id, start_time=start_time_timestamp,
                                     end_time=end_time_timestamp, temp_time_id_id=temp_id, status=True)
            time_moudel.save()
            time_moudel_info = TimeMoudelSerializer(time_moudel)
            data = time_moudel_info.data

            return JsonResponse({"code": "200", "msg": "OK", "data": data}, status=201)


class ImageInfoViewSet(viewsets.ModelViewSet):
    serializer_class = ImageInfoSerializer

    def get_queryset(self):
        now_time = datetime.datetime.now().timestamp()
        query = self.request.GET.get("query", "")
        flag = self.request.GET.get("flag", "")
        user = self.request.user
        data = TimeMoudel.objects.filter(user_id=self.request.user.id, end_time__gte=now_time).first()
        if user.is_superuser:
            if query:
                query = query.strip()
                if flag and flag == "flag":
                    image_info_list = ImageInfo.objects.filter(Q(image_name__contains=query) | Q(image_vul_name__contains=query)
                                                       | Q(image_desc__contains=query)).order_by('-create_date')
                    return image_info_list
                else:
                    image_info_list = ImageInfo.objects.filter(Q(image_name__contains=query) | Q(image_vul_name__contains=query)
                                                       | Q(image_desc__contains=query),is_ok=True).order_by('-create_date')
            else:
                if flag and flag == "flag":
                    image_info_list = ImageInfo.objects.filter().order_by('-create_date')
                    return image_info_list
                else:
                    image_info_list = ImageInfo.objects.filter(is_ok=True).order_by('-create_date')
        else:
            if query:
                query = query.strip()
                image_info_list = ImageInfo.objects.filter(Q(image_name__contains=query) | Q(image_vul_name__contains=query)
                                                       | Q(image_desc__contains=query), is_ok=True).order_by('-create_date')
            else:
                image_info_list = ImageInfo.objects.filter(is_ok=True).order_by('-create_date')
        if data:
            for image_info in image_info_list:
                image_info.image_name = ''
                image_info.image_vul_name = ''
                image_info.image_desc = ''
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
        now_time = datetime.datetime.now().timestamp()
        time_moudel_data = TimeMoudel.objects.filter(user_id=user_id, end_time__gte=now_time).first()
        time_model_id = ''
        if time_moudel_data:
            time_model_id = time_moudel_data.time_id
        container_vul = ContainerVul.objects.filter(user_id=user_id, image_id=image_id, time_model_id=time_model_id).first()
        if not container_vul:
            container_vul = ContainerVul(image_id=img_info, user_id=user_id, vul_host="", container_status="stop",
                                         docker_container_id="",
                                         vul_port="",
                                         container_port="",
                                         time_model_id=time_model_id,
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
        '''
        检测是否在时间模式中
        '''
        now_time = datetime.datetime.now().timestamp()
        time_moudel_data = TimeMoudel.objects.filter(user_id=user.id, end_time__gte=now_time).first()
        time_model_id = ''
        if time_moudel_data:
            time_model_id = time_moudel_data.time_id
        if flag == 'list' and user.is_superuser:
            if image_id:
                container_vul_list = ContainerVul.objects.filter(image_id=image_id).order_by('-create_date')
            else:
                container_vul_list = ContainerVul.objects.all().order_by('-create_date')
        else:
            container_vul_list = ContainerVul.objects.filter(user_id=user.id, time_model_id=time_model_id)
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
        
        request = self.request
        flag = request.GET.get('flag', "")
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
                # 检测是否在时间模式中
                now_time = datetime.datetime.now().timestamp()
                time_moudel_data = TimeMoudel.objects.filter(user_id=user_id, end_time__gte=now_time).first()
                if time_moudel_data:
                    rank = 0
                    time_model_id = time_moudel_data.time_id
                    successful = ContainerVul.objects.filter(is_check=True, user_id=user_id,
                                                             time_model_id=time_model_id)
                    rd = TimeRank.objects.filter(time_temp_id=time_moudel_data.temp_time_id_id, user_id=user_id).first()
                    for i in successful:
                        rank += i.image_id.rank
                    rd.rank = rank
                    rd.save()
                # 停止 Docker
                tasks.stop_container_task(container_vul=container_vul, user_info=user_info,
                                          request_ip=get_request_ip(request))
            return JsonResponse(R.ok())


class SysLogSet(viewsets.ModelViewSet):

    serializer_class = SysLogSerializer

    def get_queryset(self):
        request = self.request
        user = request.user
        query = self.request.GET.get("query", "")
        if user.is_superuser:
            return SysLog.objects.filter(Q(operation_args__contains=query) | Q(operation_name__contains=query)
                                         | Q(operation_type__contains=query) | Q(ip__contains=query)
                                         | Q(operation_value__contains=query )).order_by('-create_date')
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


class UserRank(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return UserProfile.objects.all().order_by("rank")
        else:
            return []


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

