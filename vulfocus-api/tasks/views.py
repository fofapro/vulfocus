from django.shortcuts import render
from rest_framework import viewsets
from .serializers import TaskSetSerializer
from django.http import JsonResponse
from rest_framework.decorators import action
from .models import TaskInfo
from dockerapi.common import R
from django.views.generic.base import View
import django.utils.timezone as timezone
import json
import redis
from tasks import tasks
from vulfocus.settings import REDIS_POOL
from layout_image.models import Layout
from vulfocus.settings import REDIS_POOL, client
import yaml
r = redis.Redis(connection_pool=REDIS_POOL)


class TaskSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TaskSetSerializer
    queryset = TaskInfo.objects.all().order_by('-create_date')

    @action(methods=["get"], detail=True, url_path='get')
    def get_task(self, request, pk=None):
        task_info = self.get_object()
        task_msg = task_info.task_msg
        if task_info.task_status == 1:
            return JsonResponse(R.running(msg="执行中", data=str(task_info.task_id)))
        task_info.is_show = True
        task_info.save()
        if task_msg:
            msg = json.loads(task_msg)
            if msg["status"] == 200:
                if not msg["data"]:
                    msg["data"] = {
                        "_now": int(timezone.now().timestamp())
                    }
                else:
                    msg["data"]["_now"] = int(timezone.now().timestamp())
                    try:
                        HTTP_HOST = request.META.get("HTTP_REFERER")
                        # 判断前端的请求地址是IP形式或者是域名形式
                        if HTTP_HOST.count(":") < 2:
                            HTTP_HOST = HTTP_HOST.replace("http://", "").replace("https://", "")
                            origin_host = msg["data"]["host"].split(":")
                            if len(origin_host) >= 2 and HTTP_HOST:
                                msg["data"]["host"] = HTTP_HOST[:-1] + ":" + origin_host[1]
                    except Exception as e:
                        pass
                return JsonResponse(msg, status=200)
            else:
                return JsonResponse(msg, status=200)
        return JsonResponse(R.ok())

    @action(methods=["post"], detail=True, url_path='batch')
    def get_batch_task(self, request, pk=None):
        task_id_str = request.POST.get("task_ids", "")
        task_id_list = task_id_str.split(",")
        task_list = TaskInfo.objects.filter(task_id__in=task_id_list)
        result = {}
        for task_info in task_list:
            progress = 0.0
            task_log = r.get(str(task_info.task_id))
            if task_log:
                try:
                    task_log_json = json.loads(task_log)
                    progress = task_log_json["progress"]
                except:
                    pass
            result[str(task_info.task_id)] = {
                "status": task_info.task_status,
                "data": json.loads(task_info.task_msg),
                "progress": progress
            }
        return JsonResponse(R.ok(data=result))

    @action(methods=["get"], detail=True, url_path='progress')
    def get_task_progress(self, request, pk=None):
        task_info = self.get_object()
        task_id = task_info.task_id
        task_log = r.get(str(task_id))
        if task_log:
            task_log_json = json.loads(task_log)
            data = {
                "total": task_log_json["total"],
                "progress_count": task_log_json["progress_count"],
                "progress": task_log_json["progress"],
                "layer": []
            }
            black_list = ["total", "progress_count", "progress"]
            layer_list = []
            for key in task_log_json:
                if key in black_list:
                    continue
                layer_list.append(task_log_json[key])
            data["layer"] = layer_list
            return JsonResponse(R.ok(data=data))
        else:
            return JsonResponse(R.ok())

    @action(methods=["post"], detail=True, url_path="layout_batch")
    def get_layout_batch(self, request, pk=None):
        task_id_str = request.POST.get("task_ids", "")
        task_id_list = task_id_str.split(",")
        task_list = TaskInfo.objects.filter(task_id__in=task_id_list)
        result = {}
        for task_info in task_list:
            args = task_info.operation_args
            args_info = json.loads(args)
            layout_name = args_info["layout_name"]
            image_list = []
            # 查询出该编排环境中的所有进行下载任务
            progress = 0.0
            status = 1
            relative_task_all = TaskInfo.objects.filter(operation_type=8, user_id=request.user.id,
                                                        operation_args__contains=json.dumps(layout_name), task_status=1)
            for single_task in relative_task_all:
                task_log = r.get(str(single_task.task_id))
                if task_log:
                    try:
                        task_log_json = json.loads(task_log)
                        current_progress = task_log_json["progress"]
                        progress += current_progress
                    except Exception as e:
                        pass
            layout_info = Layout.objects.filter(layout_name=layout_name).first()
            if layout_info:
                yml_data = yaml.load(layout_info.yml_content, Loader=yaml.Loader)
                services = yml_data["services"]
                for service in services:
                    image_name = services[service]["image"]
                    image_list.append(image_name)
                count = len(image_list)
                not_download = 0
                for image in image_list:
                    try:
                        current_image = client.images.get(image)
                        if current_image:
                            count -= 1
                            if count == 0:
                                status = 2
                    except Exception as e:
                        not_download += 1
            if not_download != 0:
                result[str(task_info.task_id)] = {"progress": float(progress / not_download),
                                                  "status": status}
            else:
                result[str(task_info.task_id)] = {"progress": 100.0, "status": 2}
        return JsonResponse(R.ok(data=result))


