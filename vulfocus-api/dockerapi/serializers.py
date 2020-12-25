# coding:utf-8
from django.db.models import Q
from rest_framework import serializers
from dockerapi.models import ImageInfo, ContainerVul, SysLog
from user.models import UserProfile
from tasks.models import TaskInfo
import django.utils.timezone as timezone
import json
from vulfocus.settings import REDIS_POOL
from dockerapi.common import get_setting_config
import redis
r = redis.Redis(connection_pool=REDIS_POOL)


class ImageInfoSerializer(serializers.ModelSerializer):

    status = serializers.SerializerMethodField('statusck')

    def statusck(self, obj):
        status = {}
        id = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            id = request.user.id
        '''
        检测是否在时间模式中
        '''
        time_model_id = ''
        # 排出已经删除数据 Q(docker_container_id__isnull=False), ~Q(docker_container_id=''),
        data = ContainerVul.objects.all().filter(user_id=id, image_id=obj.image_id, time_model_id=time_model_id).first()
        status["status"] = ""
        status["is_check"] = False
        status["container_id"] = ""
        status["start_date"] = ""
        status["end_date"] = ""
        status["host"] = ""
        status["port"] = ""
        status["progress"] = 0.0
        status["progress_status"] = ""
        if data:
            status["start_date"] = ""
            status["end_date"] = ""
            if not data.docker_container_id:
                data.container_status = "delete"
            if data.container_status == "running":
                status["host"] = data.vul_host
                status["port"] = data.vul_port
                operation_args = {"image_name": obj.image_name, "user_id": id, "image_port": obj.image_port}
                task_info = TaskInfo.objects.filter(user_id=id, task_status=3, operation_type=2,
                                                    operation_args=json.dumps(operation_args)).order_by("-create_date").first()
                if task_info:
                    try:
                        task_msg = json.loads(task_info.task_msg)
                        status["start_date"] = int(task_msg["data"]["start_date"])
                        status["end_date"] = int(task_msg["data"]["end_date"])
                    except:
                        status["start_date"] = ""
                        status["end_date"] = ""
            status["status"] = data.container_status
            status["is_check"] = data.is_check
            status["container_id"] = data.container_id
        # 查询正在拉取镜像的任务
        operation_args = {
            "image_name": obj.image_name
        }
        task_info = TaskInfo.objects.filter(task_status=1, operation_type=1, operation_args=json.dumps(operation_args))\
            .order_by("-create_date").first()
        if task_info:
            status["task_id"] = str(task_info.task_id)
            try:
                task_log = r.get(str(task_info.task_id))
                task_log_json = json.loads(task_log)
                status["progress"] = task_log_json["progress"]
            except:
                pass
        else:
            status["task_id"] = ""
        setting_config = get_setting_config()
        operation_args = {
            "share_username": setting_config["share_username"],
            "image_name": obj.image_name,
            "username": setting_config["username"],
            "pwd": setting_config["pwd"]
        }
        task_info = TaskInfo.objects.filter(task_status=1, operation_type=5, operation_args=json.dumps(operation_args))\
            .order_by("-create_date").first()
        if task_info:
            status["task_id"] = str(task_info.task_id)
            status["progress_status"] = "share"
            try:
                task_log = r.get(str(task_info.task_id))
                task_log_json = json.loads(task_log)
                status["progress"] = task_log_json["progress"]
            except:
                pass
        status["now"] = int(timezone.now().timestamp())
        return status

    class Meta:
        model = ImageInfo
        fields = "__all__"


class ContainerVulSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField('ranktocon')
    name = serializers.SerializerMethodField('conname')
    image_id = serializers.SerializerMethodField("get_image_id")
    user_name = serializers.SerializerMethodField('get_user_name')
    vul_name = serializers.SerializerMethodField('get_vul_name')
    vul_desc = serializers.SerializerMethodField('get_vul_desc')


    class Meta:
        model = ContainerVul
        fields = ['name', 'container_id', 'container_status', 'vul_host', 'create_date', 'is_check', 'is_check_date',
                  'rank', 'user_name', 'vul_name', 'vul_desc', "image_id"]

    def get_vul_name(self,obj):
        return obj.image_id.image_vul_name

    def get_vul_desc(self,obj):
        return obj.image_id.image_desc

    def ranktocon(self, obj):
        if obj:
            return obj.image_id.rank
        else:
            return ""

    def conname(self, obj):
        if obj:
            if obj.image_id:
                return obj.image_id.image_name
            else:
                return ""
        else:
            return ""

    def get_user_name(self, obj):
        user_id = obj.user_id
        user_info = UserProfile.objects.get(id=user_id)
        return user_info.username

    def get_image_id(self, obj):
        return str(obj.image_id.image_id)


class SysLogSerializer(serializers.ModelSerializer):

    user_name = serializers.SerializerMethodField('get_user_name')

    class Meta:
        model = SysLog
        fields = ['user_name', 'operation_type', 'operation_name', 'operation_value', 'operation_args', 'ip', 'create_date']

    def get_user_name(self, obj):
        user_id = obj.user_id
        user_info = UserProfile.objects.get(id=user_id)
        return user_info.username
