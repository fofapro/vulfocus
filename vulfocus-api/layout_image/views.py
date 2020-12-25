import random
from rest_framework import viewsets
from .serializers import LayoutSerializer
from django.core.paginator import Paginator
from .models import Layout, LayoutService, LayoutServiceNetwork, LayoutData, LayoutServiceContainer, \
    LayoutServiceContainerScore
from dockerapi.models import ImageInfo, ContainerVul, SysLog
from dockerapi.views import get_request_ip
from network.models import NetWorkInfo
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import Sum
import json
import base64
import yaml
import traceback
import django.utils.timezone as timezone
from dockerapi.common import R
from rest_framework.decorators import api_view
import os
import uuid
from vulfocus.settings import client, ALLOWED_IMG_SUFFIX, DOCKER_COMPOSE, BASE_DIR
from django.db import transaction
from .bridge import get_project
from tasks import tasks
from rest_framework.decorators import action
from user.models import UserProfile
import shutil
# Create your views here.


@api_view(http_method_names=["POST"])
def upload_img(request):
    """
    上传文件图片
    """
    user = request.user
    if not user.is_superuser:
        return JsonResponse(R.build(msg="权限不足"))
    img = request.data["img"]
    if not img:
        return JsonResponse(R.build(msg="请上传图片"))
    img_name = img.name
    img_suffix = img_name.split(".")[-1]
    if img_suffix not in ALLOWED_IMG_SUFFIX:
        return JsonResponse(R.build(msg="不支持此格式图片文件，请上传%s格式文件" % ("、".join(ALLOWED_IMG_SUFFIX),)))
    image_name = str(uuid.uuid4()).replace('-', '') + "." + img_suffix
    with open(os.path.join(BASE_DIR, "static", image_name), "wb") as f:
        for chunk in img.chunks():
            f.write(chunk)
        return JsonResponse(R.ok(data=image_name))


class LayoutViewSet(viewsets.ModelViewSet):
    serializer_class = LayoutSerializer

    def get_queryset(self):
        """
        查询
        """
        user = self.request.user
        query = self.request.GET.get("query", "")
        flag = self.request.GET.get("flag", "")
        if not flag:
            if user.is_superuser:
                pass
        else:
            pass
        if query:
            if not flag:
                if user.is_superuser:
                    return Layout.objects.filter(Q(layout_name__contains=query) | Q(layout_desc__contains=query) |
                                                 Q(raw_content__contains=query) | Q(yml_content__contains=query))\
                        .order_by('-create_date')
            return Layout.objects.filter(Q(layout_name__contains=query) | Q(layout_desc__contains=query) |
                                         Q(raw_content__contains=query) | Q(yml_content__contains=query),
                                         is_release=True).order_by('-create_date')
        else:
            if not flag:
                if user.is_superuser:
                    return Layout.objects.all().order_by('-create_date')
            return Layout.objects.filter(is_release=True).order_by('-create_date')

    def create(self, request, *args, **kwargs):
        """
        创建编排环境信息
        """
        user = request.user
        if user.is_superuser:
            data = request.POST.get("data", "")
            id = request.POST.get("id", "")
            name = request.POST.get("name", "")
            if not name:
                return JsonResponse(R.build(msg="名称不能为空"))
            desc = request.POST.get("desc", "")
            img = request.POST.get("img", "")
            if not img:
                return JsonResponse(R.build(msg="图片不能为空"))
            if not data:
                return JsonResponse(R.build(msg="参数不能为空"))
            topo_data = json.loads(data)
            if topo_data == {}:
                return JsonResponse(R.build(msg="编排环境不能为空"))
            nodes = topo_data["nodes"]
            if not nodes or len(nodes) == 0:
                return JsonResponse(R.build(msg="节点不能为空"))
            connectors = topo_data["connectors"]
            check_open = False
            container_list = []
            network_dict = {}
            check_network_name_list = []
            for node in nodes:
                node_id = node["id"]
                node_type = node["type"]
                node_attrs = node["attrs"]
                if len(node_attrs) == 0:
                    return JsonResponse(R.build(msg="节点属性不能为空"))
                if node_type == "Container":
                    node_open = node_attrs["open"]
                    node_port = node_attrs["port"]
                    if node_open and node_port:
                        check_open = True
                    container_list.append(node)
                elif node_type == "Network":
                    network_name = node_attrs["name"]
                    if not network_name:
                        return JsonResponse(R.build(msg="网卡不能为空"))
                    if network_name in check_network_name_list:
                        return JsonResponse(R.build(msg="不能重复设置网卡"))
                    check_network_name_list.append(network_name)
                    network_dict[node_id] = node
                if node_attrs == {}:
                    return JsonResponse(R.build(msg="网卡或容器属性不能为空"))
            if not check_open:
                return JsonResponse(R.build(msg="请开放可访问入口"))
            if len(container_list) == 0:
                return JsonResponse(R.build(msg="容器环境不能为空"))
            if len(network_dict) == 0:
                for container in container_list:
                    if not container["attrs"]["open"]:
                        return JsonResponse(R.build(msg="在不配置网卡段情况下请保证所有的环境开放访问权限"))
            else:
                if not connectors or len(connectors) == 0:
                    return JsonResponse(R.build(msg="在配置网卡的情况下连接点不能为空"))
            try:
                yml_content = build_yml(container_list=container_list, network_dict=network_dict,
                                        connector_list=connectors)
                yml_data = yml_content["content"]
                env_data = yml_content["env"]
                env_content = ""
                if len(env_data) > 0:
                    env_content = "\n".join(env_data)
                with transaction.atomic():
                    operation_name = "创建"
                    if id:
                        layout = Layout.objects.filter(layout_id=id).first()
                        operation_name = "修改"
                    else:
                        layout = Layout(layout_id=uuid.uuid4(), create_date=timezone.now(), update_date=timezone.now())
                    layout_data = LayoutData.objects.filter(layout_id=layout).first()
                    if layout_data and layout_data.status == 'running':
                        return JsonResponse(R.build(msg="环境正在运行中，请首先停止运行"))
                    layout.layout_name = name
                    layout.layout_desc = desc
                    layout.create_user_id = user.id
                    layout.image_name = img
                    layout.raw_content = json.dumps(topo_data, ensure_ascii=False)
                    layout.yml_content = yaml.dump(yml_content["content"])
                    layout.env_content = env_content
                    # 保存到数据库中
                    layout.save()
                    # 删除相关原有的服务数据
                    layout_service_list = list(LayoutService.objects.filter(layout_id=layout).values("service_id"))
                    # 删除网卡相关数据
                    services = yml_data["services"]
                    for service_name in services:
                        service = services[service_name]
                        image = service["image"]
                        image_info = ImageInfo.objects.filter(image_name=image).first()
                        if not image_info:
                            return JsonResponse(R.build(msg="%s 镜像不存在" % (image,)))
                        is_exposed = False
                        ports = ""
                        if "ports" in service and len(service["ports"]) > 0:
                            is_exposed = True
                        if image_info.image_port:
                            ports = ",".join(str(image_info.image_port).split(","))
                        layout_service = LayoutService.objects.filter(layout_id=layout, service_name=service_name).first()
                        if not layout_service:
                            layout_service = LayoutService(service_id=uuid.uuid4(), layout_id=layout,
                                                           service_name=service_name, create_date=timezone.now(),
                                                           update_date=timezone.now())
                        if {"service_id": layout_service.service_id} in layout_service_list:
                            layout_service_list.remove({"service_id": layout_service.service_id})
                        layout_service.image_id = image_info
                        layout_service.service_name = service_name
                        layout_service.is_exposed = is_exposed
                        layout_service.exposed_source_port = ports
                        layout_service.save()
                        if "networks" not in service:
                            continue
                        networks = service["networks"]
                        service_network_list = list(LayoutServiceNetwork.objects.filter(service_id=layout_service)
                                                    .values('layout_service_network_id'))
                        for network in networks:
                            network_info = NetWorkInfo.objects.filter(net_work_name=network).first()
                            if not network_info:
                                return JsonResponse(R.build(msg="%s 网卡不存在" % (network, )))
                            service_network = LayoutServiceNetwork.objects.filter(service_id=layout_service,
                                                                                  network_id=network_info,).first()
                            if not service_network:
                                service_network = LayoutServiceNetwork(layout_service_network_id=uuid.uuid4(),
                                                                       service_id=layout_service,
                                                                       network_id=network_info,
                                                                       create_date=timezone.now(),
                                                                       update_date=timezone.now())
                            if {"layout_service_network_id": service_network.layout_service_network_id} in service_network_list:
                                service_network_list.remove({"layout_service_network_id": service_network.
                                                            layout_service_network_id})
                            service_network.save()
                        # 删除已经不存在的网卡
                        if len(service_network_list) > 0:
                            for service_network in service_network_list:
                                LayoutServiceNetwork.objects.filter(layout_service_network_id=
                                                                    service_network['layout_service_network_id']).delete()
                    # 删除服务数据
                    for layout_service in layout_service_list:
                        service_id = layout_service['service_id']
                        # 删除服务数据
                        LayoutService.objects.filter(service_id=service_id, layout_id=layout).delete()
                        if layout_data:
                            # 删除启动容器
                            LayoutServiceContainer.objects.filter(service_id=service_id, layout_user_id=layout_data).\
                                delete()
                            # 删除分数
                            LayoutServiceContainerScore.objects.filter(layout_id=layout, layout_data_id=layout_data,
                                                                       service_id=service_id).delete()
                        else:
                            # 删除启动容器
                            LayoutServiceContainer.objects.filter(service_id=service_id).delete()
                            # 删除分数
                            LayoutServiceContainerScore.objects.filter(layout_id=layout, service_id=service_id).delete()
                    request_ip = get_request_ip(request)
                    sys_log = SysLog(user_id=user.id, operation_type="编排环境", operation_name=operation_name,
                                     operation_value=name, operation_args=json.dumps(LayoutSerializer(layout).data),
                                     ip=request_ip)
                    sys_log.save()
            except Exception as e:
                return JsonResponse(R.err(msg="服务器内部错误，请联系管理员"))
            return JsonResponse(R.ok())
        else:
            return JsonResponse(R.build(msg="权限不足"))

    def update(self, request, *args, **kwargs):
        return JsonResponse(R.ok())

    def destroy(self, request, *args, **kwargs):
        return JsonResponse(R.ok())

    @action(methods=["get"], detail=True, url_path="delete")
    def delete_image(self, request, pk=None):
        user = request.user
        if not pk or pk == "undefined":
            return JsonResponse(R.build(msg="环境不存在"))
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足"))
        try:
            layout = Layout.objects.filter(layout_id=pk).first()
            if not layout:
                return JsonResponse(R.build(msg="环境不存在"))
            layout_name = layout.layout_name
            layout_id = str(layout.layout_id)
            layout_path = os.path.join(DOCKER_COMPOSE, layout_id)
            with transaction.atomic():
                _tmp_file_path = "docker-compose"+layout_path.replace(DOCKER_COMPOSE, "")
                layout_data = LayoutData.objects.filter(layout_id=layout, file_path=_tmp_file_path).first()
                if layout_data and layout_data.status == 'running':
                    return JsonResponse(R.build(msg="环境正在运行中，请首先停止运行"))
                # 删除分数
                LayoutServiceContainerScore.objects.filter(layout_id=layout).delete()
                # 删除容器
                if layout_data:
                    LayoutServiceContainer.objects.filter(layout_user_id=layout_data)
                # 删除服务网卡
                service_list = LayoutService.objects.filter(layout_id=layout)
                if len(service_list) > 0:
                    for service in service_list:
                        # service_id = service.service_id
                        LayoutServiceNetwork.objects.filter(service_id=service).delete()
                # 删除服务
                LayoutService.objects.filter(layout_id=layout).delete()
                # 删除内容
                layout.delete()
                # 删除文件和文件夹
                shutil.rmtree(layout_path)
                request_ip = get_request_ip(request)
                sys_log = SysLog(user_id=user.id, operation_type="编排环境", operation_name="删除",
                                 operation_value=layout_name, operation_args=json.dumps(LayoutSerializer(layout).data),
                                 ip=request_ip)
                sys_log.save()
        except Exception as e:
            traceback.print_exc()
            return JsonResponse(R.err())
        return JsonResponse(R.ok())

    @action(methods=["get"], detail=True, url_path="get")
    def get_layout(self, request, pk=None):
        if not pk or pk == "undefined":
            return JsonResponse(R.build(msg="环境不存在"))
        user = request.user
        if user.is_superuser:
            layout_info = Layout.objects.filter(layout_id=pk).first()
        else:
            layout_info = Layout.objects.filter(layout_id=pk, is_release=True).first()
        if not layout_info:
            return JsonResponse(R.build(msg="环境不存在或未发布"))
        layout_path = os.path.join(DOCKER_COMPOSE, str(layout_info.layout_id))
        layout_data = LayoutData.objects.filter(layout_id=layout_info,
                                                file_path="docker-compose" + layout_path.replace(DOCKER_COMPOSE,
                                                                                                 ""), ).first()
        open_host_list = []
        is_run = False
        if layout_data and layout_data.status == 'running':
            service_container_list = LayoutServiceContainer.objects.filter(layout_user_id=layout_data)
            for service_container in service_container_list:
                service_info = service_container.service_id
                container_host = service_container.container_host
                if service_info.is_exposed:
                    if container_host:
                        open_host_list.extend(container_host.split(","))
            is_run = True
        result_data = {
            "layout": {
                "name": layout_info.layout_name,
                "desc": layout_info.layout_desc,
            },
            "open": open_host_list,
            "is_run": is_run
        }
        return JsonResponse(R.ok(data=result_data))

    @action(methods=["get"], detail=True, url_path="start")
    def run_layout(self, request, pk=None):
        if not pk or pk == "undefined":
            return JsonResponse(R.build(msg="环境不存在"))
        """
        运行环境
        """
        user = request.user
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足"))
        layout_info = Layout.objects.filter(layout_id=pk, is_release=True).first()
        if not layout_info:
            return JsonResponse(R.build(msg="环境不存在或未发布"))
        yml_content = layout_info.yml_content
        env_content = layout_info.env_content
        layout_id = str(layout_info.layout_id)
        layout_path = os.path.join(DOCKER_COMPOSE, layout_id)
        try:
            env_content = get_random_port(env_content)
        except Exception as e:
            return JsonResponse(R.build(msg=str(e)))
        open_host_list = []
        try:
            with transaction.atomic():
                _tmp_file_path = "docker-compose"+layout_path.replace(DOCKER_COMPOSE, "")
                layout_data = LayoutData.objects.filter(layout_id=layout_info, file_path=_tmp_file_path).first()
                if not layout_data:
                    layout_data = LayoutData(layout_user_id=uuid.uuid4(), create_user_id=user.id, layout_id=layout_info,
                                             status="running",
                                             file_path="docker-compose"+layout_path.replace(DOCKER_COMPOSE, ""),
                                             create_date=timezone.now(), update_date=timezone.now())
                else:
                    layout_data.status = "running"
                if not os.path.exists(layout_path):
                    os.mkdir(layout_path)
                docker_compose_file = os.path.join(layout_path, "docker-compose.yml")
                with open(docker_compose_file, "w", encoding="utf-8") as f:
                        f.write(yml_content)
                env_file = os.path.join(layout_path, ".env")
                with open(env_file, "w", encoding="utf-8") as f:
                        f.write("\n".join(env_content))
                # 启动
                container_list = get_project(layout_path).up()
                # 保存
                layout_data.save()
                for container in container_list:
                    docker_container_id = container.id
                    service_id = container.service
                    container_host = ""
                    container_port = ""
                    container_flag = "flag-{bmh%s}" % (uuid.uuid4(),)
                    docker_container = client.containers.get(container.id)
                    service_info = LayoutService.objects.filter(service_name=service_id, layout_id=layout_info).first()
                    if not service_info:
                        raise Exception("环境服务不存在")
                    image_info = service_info.image_id
                    service_container = LayoutServiceContainer.objects.filter(service_id=service_info, user_id=user.id,
                                                                              layout_user_id=layout_data,
                                                                              image_id=image_info).first()
                    if not service_container:
                        service_container = LayoutServiceContainer(service_container_id=uuid.uuid4(), user_id=user.id,
                                                                   service_id=service_info, layout_user_id=layout_data,
                                                                   image_id=image_info,
                                                                   container_flag=container_flag,
                                                                   create_date=timezone.now())
                    else:
                        container_flag = service_container.container_flag
                    """
                    写入 flag
                    """
                    command = 'touch /tmp/%s' % (container_flag,)
                    execute_result = tasks.docker_container_run(docker_container, command)
                    if execute_result["status"] == 500:
                        raise Exception(execute_result["msg"])
                    container_ports = container.ports
                    if len(container_ports) == 0:
                        try:
                            container_ports = docker_container.attrs["NetworkSettings"]["Ports"]
                        except Exception as e:
                            pass
                    vul_host_list = []
                    if service_info.is_exposed:
                        vul_ip = tasks.get_local_ip()
                    else:
                        vul_ip = "127.0.0.1"
                    port_dict = {
                    }
                    if len(container_ports) > 0:
                        for _tmp_port in container_ports:
                            source_port = str(_tmp_port).replace("/", "").replace("tcp", "").replace("udp", "")
                            if container_ports[_tmp_port]:
                                target_port = container_ports[_tmp_port][0]["HostPort"]
                            else:
                                target_port = source_port
                            port_dict[source_port] = target_port
                            vul_host_list.append(vul_ip+":"+target_port)
                    if len(vul_host_list) > 0:
                        container_host = ",".join(vul_host_list)
                        if service_info.is_exposed:
                            open_host_list.extend(vul_host_list)
                    if len(port_dict) > 0:
                        container_port = json.dumps(port_dict, ensure_ascii=False)
                    # 连接 host
                    service_container.container_host = container_host
                    # 连接 端口
                    service_container.container_port = container_port
                    container_status = execute_result["data"]["status"]
                    service_container.docker_container_id = docker_container_id
                    service_container.container_status = container_status
                    service_container.update_date = timezone.now()
                    service_container.save()
        except Exception as e:
            return JsonResponse(R.build(msg=str(e)))
        result_data = {
            "layout": {
                "name": layout_info.layout_name,
                "desc": layout_info.layout_desc,
            },
            "open": open_host_list
        }
        request_ip = get_request_ip(request)
        sys_log = SysLog(user_id=user.id, operation_type="编排环境", operation_name="启动",
                         operation_value=layout_info.layout_name, operation_args=json.dumps(LayoutSerializer(layout_info).data),
                         ip=request_ip)
        sys_log.save()
        return JsonResponse(R.ok(data=result_data))

    @action(methods=["get"], detail=True, url_path="stop")
    def stop_layout(self, request, pk=None):
        if not pk or pk == "undefined":
            return JsonResponse(R.build(msg="环境不存在"))
        user = request.user
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足"))
        layout_info = Layout.objects.filter(layout_id=pk, is_release=True).first()
        if not layout_info:
            return JsonResponse(R.build(msg="环境不存在或未发布"))
        layout_id = str(layout_info.layout_id)
        layout_path = os.path.join(DOCKER_COMPOSE, layout_id)
        layout_data = LayoutData.objects.filter(layout_id=layout_info,
                                                file_path="docker-compose" + layout_path.replace(DOCKER_COMPOSE,
                                                                                                 ""), ).first()
        if not layout_data:
            return JsonResponse(R.build(msg="环境未启动，无法停止"))
        if not os.path.exists(layout_path):
            return JsonResponse(R.ok())
        if layout_data.status == "stop":
            return JsonResponse(R.ok())
        try:
            with transaction.atomic():
                container_list = get_project(layout_path).stop()
                if container_list:
                    for container in container_list:
                        container_id = container.id
                        LayoutServiceContainer.objects.filter(docker_container_id=container_id)\
                            .update(container_status="stop")
                LayoutServiceContainer.objects.filter(layout_user_id=layout_data).update(container_status="stop")
                layout_data.status = "stop"
                layout_data.save()
        except Exception as e:
            return JsonResponse(R.err())
        request_ip = get_request_ip(request)
        sys_log = SysLog(user_id=user.id, operation_type="编排环境", operation_name="停止",
                         operation_value=layout_info.layout_name, operation_args=json.dumps(LayoutSerializer(layout_info).data),
                         ip=request_ip)
        sys_log.save()
        return JsonResponse(R.ok())

    @action(methods=["get"], detail=True, url_path="flag")
    def flag_layout(self, request, pk=None):
        if not pk or pk == "undefined":
            return JsonResponse(R.build(msg="环境不存在"))
        user = request.user
        layout_info = Layout.objects.filter(layout_id=pk, is_release=True).first()
        if not layout_info:
            return JsonResponse(R.build(msg="环境不存在或未发布"))
        flag = str(request.GET.get("flag", ""))
        if not flag:
            return JsonResponse(R.build(msg="Flag 不能为空"))
        if not flag.startswith("flag-{bmh"):
            return JsonResponse(R.build(msg="Flag 格式不正确"))
        layout_path = os.path.join(DOCKER_COMPOSE, str(layout_info.layout_id))
        layout_data = LayoutData.objects.filter(layout_id=layout_info,
                                                file_path="docker-compose" + layout_path.replace(DOCKER_COMPOSE,
                                                                                                 ""), ).first()
        service_container = LayoutServiceContainer.objects.filter(layout_user_id=layout_data,
                                                                  container_flag=flag).first()
        if not service_container:
            return JsonResponse(R.build(msg="Flag 不正确"))
        service_container_score = LayoutServiceContainerScore.objects.filter(user_id=user.id, flag=flag,
                                                                             service_container_id=service_container).first()
        if not service_container_score:
            service_info = service_container.service_id
            image_info = service_container.image_id
            service_container_score = LayoutServiceContainerScore(layout_service_container_score_id=uuid.uuid4(),
                                                                  user_id=user.id, layout_id=layout_info,
                                                                  layout_data_id=layout_data, service_id=service_info,
                                                                  image_id=image_info, create_date=timezone.now(),
                                                                  service_container_id=service_container, flag=flag,
                                                                  update_date=timezone.now())
        service_container_score.save()
        request_ip = get_request_ip(request)
        sys_log = SysLog(user_id=user.id, operation_type="编排环境", operation_name="提交Flag",
                         operation_value=layout_info.layout_name, operation_args=json.dumps({"flag": flag}),
                         ip=request_ip)
        sys_log.save()
        return JsonResponse(R.ok())

    @action(methods=["get"], detail=True, url_path="rank")
    def rank_layout(self, request, pk=None):
        """
        排行
        """
        user = request.user
        page_no = int(request.GET.get("page", 1))
        if not pk or pk == "undefined":
            return JsonResponse(R.build(msg="环境不存在"))
        layout_info = Layout.objects.filter(layout_id=pk, is_release=True).first()
        if not layout_info:
            return JsonResponse(R.build(msg="环境不存在"))
        score_list = LayoutServiceContainerScore.objects.filter(layout_id=layout_info).values('user_id').annotate(
            score=Sum("image_id__rank")).values('user_id', 'score').order_by("-score")
        try:
            pages = Paginator(score_list, 20)
            page = pages.page(page_no)
        except Exception as e:
            return JsonResponse(R.err())
        current_rank = 0
        current_score = 0
        for i, _score in enumerate(score_list):
            user_id = _score["user_id"]
            if user.id != user_id:
                continue
            current_rank = i+1
            current_score = _score["score"]
            break
        layout_path = os.path.join(DOCKER_COMPOSE, str(layout_info.layout_id))
        layout_data = LayoutData.objects.filter(layout_id=layout_info,
                                                file_path="docker-compose" + layout_path.replace(DOCKER_COMPOSE,
                                                                                                 ""), ).first()
        score_count = LayoutServiceContainerScore.objects.filter(layout_id=layout_info, user_id=user.id).count()
        score_total_count = LayoutServiceContainer.objects.filter(layout_user_id=layout_data).count()
        result = []
        for _data in list(page):
            user_info = UserProfile.objects.filter(id=_data["user_id"]).first()
            username = ""
            if user_info:
                username = user_info.username
            result.append({"score": _data["score"], "username": username})
        return JsonResponse({
            "result": result,
            "count": pages.count,
            "current": current_rank,
            "progress": "%s/%s" % (score_count, score_total_count,),
            "score": current_score
        })

    @action(methods=["get"], detail=True, url_path="release")
    def release_layout(self, request, pk=None):
        """
        发布环境
        """
        if not pk or pk == "undefined":
            return JsonResponse(R.build(msg="环境不存在"))
        user = request.user
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足"))
        layout_info = Layout.objects.filter(layout_id=pk).first()
        if not layout_info:
            return JsonResponse(R.build(msg="环境不存在"))
        layout_info.is_release = True
        layout_info.save()
        return JsonResponse(R.ok())


def get_random_port(env_content):
    """
    生成随机端口列表
    """
    random_list = []
    result_port_list = []
    for _port in env_content.split("\n"):
        random_port = ''
        for i in range(20):
            random_port = str(random.randint(8000, 65536))
            if random_port in random_list or ContainerVul.objects.filter(container_port=random_port).first():
                continue
            break
        if not random_port:
            raise Exception("无可用端口")
        random_list.append(random_port)
        result_port_list.append("%s=%s" % (_port, random_port,))
    return result_port_list


def build_yml(container_list, network_dict, connector_list):
    yml_data = {}
    services = {}
    all_network = {}
    env_list = []
    # 环境列表
    image_list = []
    for id in network_dict:
        network_name = network_dict[id]["attrs"]["name"]
        all_network[network_name] = {"external": True}
    # open
    for container in container_list:
        id = container["id"]
        attrs = container["attrs"]
        image_name = attrs["name"]
        open = attrs["open"]
        port = attrs["port"]
        port_list = []
        network_list = []
        if open and port:
            for _port in port.split(","):
                base_target_port = id+"-"+_port
                encode_base_target_port = base64.b64encode(base_target_port.encode("utf-8"))
                encode_base_target_port = "VULFOCUS"+encode_base_target_port.hex().upper()
                if encode_base_target_port not in env_list:
                    env_list.append(encode_base_target_port)
                port_str = "${"+encode_base_target_port+"}:"+_port+""
                port_list.append(port_str)
        services[id] = {
            "image": image_name
        }
        if len(port_list) > 0:
            services[id]["ports"] = port_list
        for connector in connector_list:
            target_node = connector["targetNode"]
            target_node_id = target_node["id"]
            source_node = connector["sourceNode"]
            source_node_id = source_node["id"]
            network = None
            if target_node_id == id:
                network = network_dict[source_node_id]["attrs"]["name"]
            elif source_node_id == id:
                network = network_dict[target_node_id]["attrs"]["name"]
            if network:
                network_list.append(network)
        if len(network_list) > 0:
            services[id]["networks"] = network_list
        image_list.append({
            "open": open,
            "image_id": attrs["id"],
            "networks": network_list
        })
    yml_data["version"] = "3.2"
    yml_data["services"] = services
    if len(all_network) > 0:
        yml_data["networks"] = all_network
    yml_content = {
        "content": yml_data,
        "env": env_list,
    }
    return yml_content
