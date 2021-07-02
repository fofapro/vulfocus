# coding:utf-8
from django.db.models import Q
import traceback
from rest_framework import serializers
from dockerapi.models import ImageInfo, ContainerVul, SysLog, TimeMoudel, TimeRank, TimeTemp
from user.models import UserProfile
from tasks.models import TaskInfo
import django.utils.timezone as timezone
import json
from vulfocus.settings import REDIS_POOL
from dockerapi.common import get_setting_config
import redis
import time
import datetime
r = redis.Redis(connection_pool=REDIS_POOL)


class TimeTempSerializer(serializers.ModelSerializer):
    time_img_type = serializers.SerializerMethodField('typeck')
    rank_range = serializers.SerializerMethodField('rankck')

    def typeck(self, obj):
        img_d = obj.time_img_type
        try:
            return json.loads(img_d)
        except Exception as e:
            return []

    def rankck(self, obj):
        # rank = obj.rank_range
        if obj.rank_range != "":
            try:
                return float(obj.rank_range)
            except Exception as e:
                return 0.0

    class Meta:
        model = TimeTemp
        fields = "__all__"


class TimeRankSerializer(serializers.ModelSerializer):
    flag_s = serializers.SerializerMethodField('flag_status')
    name = serializers.SerializerMethodField("a_user_name")

    class Meta:
        model = TimeRank
        fields = "__all__"

    def flag_status(self, obj):
        flag = ""
        return str(flag)

    def a_user_name(self, obj):
        name = obj.user_name
        return name

class TimeMoudelSerializer(serializers.ModelSerializer):

    start_date = serializers.SerializerMethodField('a_start_date')
    end_date = serializers.SerializerMethodField('a_end_date')

    class Meta:
        model = TimeMoudel
        fields = ['start_date', 'end_date', "temp_time_id"]

    def a_start_date(self, obj):
        time_stamp = obj.start_time
        time_arr = time.localtime(time_stamp)
        return str(time.strftime("%Y-%m-%d %H:%M:%S", time_arr))

    def a_end_date(self, obj):
        time_stamp = obj.end_time
        time_arr = time.localtime(time_stamp)
        return str(time.strftime("%Y-%m-%d %H:%M:%S", time_arr))


class ImageInfoSerializer(serializers.ModelSerializer):

    status = serializers.SerializerMethodField('statusck')
    degree = serializers.SerializerMethodField('degreeck')
    writeup_date = serializers.SerializerMethodField('contentck')
    update_date = serializers.SerializerMethodField('transition_time')

    def statusck(self, obj):
        status = {}
        id = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            id = request.user.id
        '''
        检测是否在时间模式中
        '''
        now_time = datetime.datetime.now().timestamp()
        time_moudel_data = TimeMoudel.objects.filter(user_id=id, end_time__gte=now_time).first()
        time_model_id = ''
        if time_moudel_data:
            time_model_id = time_moudel_data.time_id
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

    def degreeck(self, obj):
        img_d = obj.degree
        try:
            return json.loads(img_d)
        except Exception as e:
            return []

    def contentck(self, obj):
        content = obj.writeup_date
        try:
            return json.loads(content)
        except Exception as e:
            return ""

    def transition_time(self,obj):
        time = obj.update_date.strftime('%Y-%m-%d %H:%M:%S')
        return time

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
    create_date = serializers.SerializerMethodField('transition_time')


    class Meta:
        model = SysLog
        fields = ['user_name', 'operation_type', 'operation_name', 'operation_value', 'operation_args', 'ip', 'create_date']

    def get_user_name(self, obj):
        user_id = obj.user_id
        user_info = UserProfile.objects.get(id=user_id)
        return user_info.username

    def transition_time(self,obj):
        time = obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
        return time