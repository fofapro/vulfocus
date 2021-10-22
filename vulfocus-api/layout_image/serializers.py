# coding:utf-8
from rest_framework import serializers
from layout_image.models import Layout, LayoutService, LayoutServiceNetwork, LayoutServiceContainer, LayoutData
from tasks.models import TaskInfo
import json
import redis
import yaml
from vulfocus.settings import REDIS_POOL, client
r = redis.Redis(connection_pool=REDIS_POOL)

class LayoutSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField("statusck")

    def statusck(self, obj):
        status = {}
        status["task_id"] = ""
        status["progress"] = 0.0
        user_id = obj.create_user_id
        not_download_count = 0
        # 查询所有正在下载镜像的task任务
        task_infos = TaskInfo.objects.filter(user_id=user_id, task_status=1, operation_type=8,
                                            operation_args__contains=json.dumps(obj.layout_name)).all()
        task_list = []
        for single_task in task_infos:
            task_list.append(str(single_task.task_id))
        if len(task_list) > 0:
            status["task_id"] = str(task_list[0])
        current_progress = 0.0
        try:
            for single_task in task_infos:
                task_log = r.get(str(single_task.task_id))
                task_log_json = json.loads(task_log)
                current_progress += task_log_json["progress"]
        except Exception as e:
            pass
        if len(task_list) > 0:
            status["progress"] = float(current_progress / (len(task_list)))
        if not task_infos:
            status["progress"] = 100.0
        try:
            yml_data = yaml.load(obj.yml_content, Loader=yaml.Loader)
            image_list = []
            services = yml_data["services"]
            for service in services:
                image_name = services[service]["image"]
                image_list.append(image_name)
            count = len(image_list)
            for image in image_list:
                try:
                    current_image = client.images.get(image)
                    if current_image:
                        count -= 1
                except Exception as e:
                    pass
            if count == 0:
                status["task_id"] = ""
                status["progress"] = 100.0
        except Exception as e:
            pass
        return status
    class Meta:
        model = Layout
        fields = ["layout_id", "layout_name", "layout_desc", "image_name", "create_user_id", "is_release",
                  "raw_content", "yml_content", "env_content", "create_date", "update_date", "is_uesful",
                  "status", "total_view", "download_num"]


class LayoutServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = LayoutService
        fields = "__all__"


class LayoutServiceNetworkSerializer(serializers.ModelSerializer):

    class Meta:
        model = LayoutServiceNetwork
        fields = "__all__"


class LayoutServiceContainerSerializer(serializers.ModelSerializer):

    class Meta:
        model = LayoutServiceContainer
        fields = "__all__"


class LayoutDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = LayoutData
        fields = "__all__"

