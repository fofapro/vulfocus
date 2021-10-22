import random
from rest_framework import viewsets
from .serializers import LayoutSerializer
from django.core.paginator import Paginator
from .models import Layout, LayoutService, LayoutServiceNetwork, LayoutData, LayoutServiceContainer, \
    LayoutServiceContainerScore, SceneUserFav
from django.views.decorators.csrf import csrf_exempt
from dockerapi.models import ImageInfo, ContainerVul, SysLog, TimeTemp, TimeRank, TimeMoudel
from dockerapi.serializers import TimeTempSerializer
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
from vulfocus.settings import client, ALLOWED_IMG_SUFFIX, DOCKER_COMPOSE, BASE_DIR, COMPOSE_ZIP_PATH, DOWNLOAD_FILE_TYPE, UPLOAD_ZIP_PATH
from django.db import transaction
from .bridge import get_project
from tasks import tasks
from rest_framework.decorators import action
from user.models import UserProfile
import shutil
import docker
from tasks.models import TaskInfo
from tasks import tasks
from tasks.serializers import TaskSetSerializer
from django.http import StreamingHttpResponse
import yaml
import sys
if sys.version_info >= (3,6):
    import zipfile
else:
    import zipfile36 as zipfile
import requests
# Create your views here.


@api_view(http_method_names=["POST"])
def upload_img(request):
    """
    上传文件图片
    """
    user = request.user
    if not user.is_superuser:
        return JsonResponse(R.build(msg="权限不足"))
    try:
        img = request.data["img"]
    except:
        return JsonResponse(R.build(msg="上传失败"))
    if not img:
        return JsonResponse(R.build(msg="请上传图片"))
    img_name = img.name
    img_suffix = img_name.split(".")[-1]
    if img_suffix not in ALLOWED_IMG_SUFFIX:
        return JsonResponse(R.build(msg="不支持此格式图片文件，请上传%s格式文件" % ("、".join(ALLOWED_IMG_SUFFIX),)))
    image_name = str(uuid.uuid4()).replace('-', '') + "." + img_suffix
    static_path = os.path.join(BASE_DIR, "static")
    if not os.path.exists(static_path):
        os.mkdir(static_path)
    with open(os.path.join(BASE_DIR, "static", image_name), "wb") as f:
        for chunk in img.chunks():
            f.write(chunk)
        return JsonResponse(R.ok(data=image_name))


@api_view(http_method_names=["POST"])
def upload_file(request):
    """
    上传文件
    """
    user = request.user
    if not user.is_superuser:
        return JsonResponse(R.build(msg="权限不足"))
    file = request.data["file"]
    if not file:
        return JsonResponse(R.build(msg="请上传文件"))
    file_name = file.name
    compose_v = os.path.join(DOCKER_COMPOSE, 'compose_file')
    if not os.path.exists(compose_v):
        os.makedirs(compose_v)
    files = []
    for path, dirs, files in os.walk(compose_v):
        files = files
    if file_name in files:
        return JsonResponse(R.build(msg="文件名重复，请更改！"))
    try:
        with open(os.path.join(DOCKER_COMPOSE, "compose_file", file_name), "wb") as f:
            for chunk in file.chunks():
                f.write(chunk)
    except Exception as e:
        return JsonResponse(R.build(msg="上传失败"))
    data = {"data": file_name, 'filePath': compose_v}
    return JsonResponse(R.ok(data=data))


@api_view(http_method_names=["POST"])
def delete_file(request):
    """
    删除文件
    """
    user = request.user
    if not user.is_superuser:
        return JsonResponse(R.build(msg="权限不足"))
    file = request.data["file"]
    if not file:
        return JsonResponse(R.build(msg="删除失败"))
    file_name = file
    if '../compose_file/' in file_name:
        file_name = file_name.replace('../compose_file/','')
    static_path = os.path.join(DOCKER_COMPOSE, "compose_file")
    delete_name = static_path + '/' + file_name
    try:
        os.remove(delete_name)
    except Exception as e:
        return JsonResponse(R.build(msg="删除失败"))
    return JsonResponse(R.ok(data='删除成功'))


class LayoutViewSet(viewsets.ModelViewSet):
    serializer_class = LayoutSerializer

    def get_queryset(self):
        """
        查询
        """
        user = self.request.user
        layout_id = self.request.GET.get("id", "")
        if layout_id:
            if not user.is_superuser:
                return JsonResponse(R.err("权限不够"))
            else:
                layout_info = Layout.objects.filter(layout_id=layout_id)
                return layout_info
        # query = self.request.GET.get("query", "")
        # flag = self.request.GET.get("flag", "")
        # if not flag:
        #     if user.is_superuser:
        #         pass
        # else:
        #     pass
        # if query:
        #     if not flag:
        #         if user.is_superuser:
        #             return Layout.objects.filter(Q(layout_name__contains=query) | Q(layout_desc__contains=query) |
        #                                          Q(raw_content__contains=query) | Q(yml_content__contains=query)) \
        #                 .order_by('-create_date')
        #     return Layout.objects.filter(Q(layout_name__contains=query) | Q(layout_desc__contains=query) |
        #                                  Q(raw_content__contains=query) | Q(yml_content__contains=query),
        #                                  is_release=True).order_by('-create_date')
        # else:
        #     if not flag:
        #         if user.is_superuser:
        #             return Layout.objects.all().order_by('-create_date')
        #     return Layout.objects.filter(is_release=True).order_by('-create_date')

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
                        layout_service = LayoutService.objects.filter(layout_id=layout,
                                                                      service_name=service_name).first()
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
                                return JsonResponse(R.build(msg="%s 网卡不存在" % (network,)))
                            service_network = LayoutServiceNetwork.objects.filter(service_id=layout_service,
                                                                                  network_id=network_info, ).first()
                            if not service_network:
                                service_network = LayoutServiceNetwork(layout_service_network_id=uuid.uuid4(),
                                                                       service_id=layout_service,
                                                                       network_id=network_info,
                                                                       create_date=timezone.now(),
                                                                       update_date=timezone.now())
                            if {
                                "layout_service_network_id": service_network.layout_service_network_id} in service_network_list:
                                service_network_list.remove({"layout_service_network_id": service_network.
                                                            layout_service_network_id})
                            service_network.save()
                        # 删除已经不存在的网卡
                        if len(service_network_list) > 0:
                            for service_network in service_network_list:
                                LayoutServiceNetwork.objects.filter(layout_service_network_id=
                                                                    service_network[
                                                                        'layout_service_network_id']).delete()
                    # 删除服务数据
                    for layout_service in layout_service_list:
                        service_id = layout_service['service_id']
                        # 删除服务数据
                        LayoutService.objects.filter(service_id=service_id, layout_id=layout).delete()
                        if layout_data:
                            # 删除启动容器
                            LayoutServiceContainer.objects.filter(service_id=service_id, layout_user_id=layout_data). \
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
                _tmp_file_path = "docker-compose" + layout_path.replace(DOCKER_COMPOSE, "")
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
                if os.path.exists(layout_path) == True:
                    shutil.rmtree(layout_path)
                request_ip = get_request_ip(request)
                sys_log = SysLog(user_id=user.id, operation_type="编排环境", operation_name="删除",
                                 operation_value=layout_name, operation_args=json.dumps({}),
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
        layout_info.total_view += 1
        layout_info.save()
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
                "image_name": layout_info.image_name
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
        # 启动网卡
        raw_con = json.loads(layout_info.raw_content)
        network_list = client.networks.list()
        net_list = []
        network_names = [item['attrs']['name'] for item in raw_con['nodes'] if item['name'] == "Network"]
        for i in network_list:
            net_list.append(i.attrs['Name'])
        for network_name in network_names:
            if network_name in net_list:
                pass
            else:
                try:
                    network_det = NetWorkInfo.objects.filter(net_work_name=network_name).first()
                    ipam_pool = docker.types.IPAMPool(
                        subnet=network_det.net_work_subnet,
                        gateway=network_det.net_work_gateway
                    )
                    ipam_config = docker.types.IPAMConfig(
                        pool_configs=[ipam_pool]
                    )
                    net_work = client.networks.create(
                        network_det.net_work_name,
                        driver=network_det.net_work_driver,
                        ipam=ipam_config,
                        scope=network_det.net_work_scope
                    )
                    net_work_client_id = str(net_work.id)
                    if not network_det.net_work_gateway:
                        net_work_gateway = net_work.attrs['IPAM']['Config']['Gateway']
                        network_det.net_work_gateway = net_work_gateway
                    network_det.net_work_client_id = net_work_client_id
                    network_det.save()
                except Exception as e:
                    return JsonResponse(R.build(msg=str(e)))
        try:
            with transaction.atomic():
                _tmp_file_path = "docker-compose" + layout_path.replace(DOCKER_COMPOSE, "")
                layout_data = LayoutData.objects.filter(layout_id=layout_info, file_path=_tmp_file_path).first()
                if not layout_data:
                    layout_data = LayoutData(layout_user_id=uuid.uuid4(), create_user_id=user.id, layout_id=layout_info,
                                             status="running",
                                             file_path="docker-compose" + layout_path.replace(DOCKER_COMPOSE, ""),
                                             create_date=timezone.now(), update_date=timezone.now())
                else:
                    layout_data.status = "running"
                if not os.path.exists(layout_path):
                    os.makedirs(layout_path)
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
                            vul_host_list.append(vul_ip + ":" + target_port)
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
            traceback.print_exc()
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
                         operation_value=layout_info.layout_name,
                         operation_args=json.dumps(LayoutSerializer(layout_info).data),
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
                        LayoutServiceContainer.objects.filter(docker_container_id=container_id) \
                            .update(container_status="stop")
                LayoutServiceContainer.objects.filter(layout_user_id=layout_data).update(container_status="stop")
                layout_data.status = "stop"
                layout_data.save()
        except Exception as e:
            return JsonResponse(R.err())
        request_ip = get_request_ip(request)
        sys_log = SysLog(user_id=user.id, operation_type="编排环境", operation_name="停止",
                         operation_value=layout_info.layout_name,
                         operation_args=json.dumps(LayoutSerializer(layout_info).data),
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
            current_rank = i + 1
            current_score = _score["score"]
            break
        layout_path = os.path.join(DOCKER_COMPOSE, str(layout_info.layout_id))
        layout_data = LayoutData.objects.filter(layout_id=layout_info,
                                                file_path="docker-compose" + layout_path.replace(DOCKER_COMPOSE,
                                                                                                 ""), ).first()
        score_count = LayoutServiceContainerScore.objects.filter(layout_id=layout_info, user_id=user.id).count()
        score_total_count = LayoutServiceContainer.objects.filter(layout_user_id=layout_data).count()
        layout_all_img = LayoutServiceContainer.objects.filter(layout_user_id=layout_data)
        total_all_score = 0
        for i in layout_all_img:
            rank = i.image_id.rank
            total_all_score += int(rank)
        result = []
        adopt_count = 0
        for _data in list(page):
            user_info = UserProfile.objects.filter(id=_data["user_id"]).first()
            username = ""
            user_avatar = ""
            if user_info:
                username = user_info.username
                user_avatar = user_info.avatar
            if _data["score"] >= total_all_score:
                adopt_count += 1
            result.append({"score": _data["score"], "username": username, "user_avatar": user_avatar})
            # round(psutil.virtual_memory().total / 1073741824, 2)
        if score_count == 0:
            score = 0
        else:
            score = (round(score_count / score_total_count, 2) * 100)
        return JsonResponse({
            "result": result,
            "count": pages.count,
            "current": current_rank,
            # "progress": "%s/%s" % (score_count, score_total_count,),
            "progress": "%s" % score,
            "score": current_score,
            "adopt_count": adopt_count
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

    @action(methods=["get"], detail=True, url_path="download")
    def download_layout(self, request, pk=None):
        """
        下载环境编排压缩包
        :param request:
        :param pk:
        :return:
        """
        if not pk:
            return JsonResponse(R.build(msg="环境不存在"))
        user = request.user
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足"))
        layout_instance = Layout.objects.filter(layout_id=pk).first()
        if not layout_instance:
            return JsonResponse(R.build(msg="环境不存在"))
        zip_file_path = os.path.join(COMPOSE_ZIP_PATH, str(layout_instance.layout_name))
        if not os.path.exists(zip_file_path):
            os.makedirs(zip_file_path)
        raw_path = os.path.join(zip_file_path, "raw-content.json")
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(layout_instance.raw_content)
        layout_info = {}
        layout_info["layout_name"] = layout_instance.layout_name
        layout_info["layout_desc"] = layout_instance.layout_desc
        layout_info_path = os.path.join(zip_file_path, "layout_info.json")
        with open(layout_info_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(layout_info))
        image_path = os.path.join(zip_file_path, layout_instance.image_name)
        with open(os.path.join(BASE_DIR, 'static', layout_instance.image_name), "rb") as f:
            download_image = open(image_path, "wb")
            download_image.write(f.read())
            download_image.close()
        download_zip = zipfile.ZipFile("{}.zip".format(zip_file_path), "w", zipfile.ZIP_DEFLATED)
        download_zip.write(filename=raw_path, arcname="{dir_path}/raw-content.json".format(dir_path=layout_instance.layout_name))
        download_zip.write(filename=image_path, arcname="{dir_path}/{image_name}".format(dir_path=layout_instance.layout_name, image_name=layout_instance.image_name))
        download_zip.write(filename=layout_info_path, arcname="{dir_path}/layout_info.json".format(dir_path=layout_instance.layout_name))
        download_zip.close()
        response = StreamingHttpResponse(file_iterator("{}.zip".format(zip_file_path)))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename={file_name}{format}'.format(
            file_name=layout_instance.layout_name, format=DOWNLOAD_FILE_TYPE)
        return response

    @action(methods=["post"], detail=True, url_path="update_desc")
    def update_layout_desc(self, request, pk=None):
        if not pk:
            return JsonResponse(R.build(msg="环境不存在"))
        user = request.user
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足"))
        layout_info = Layout.objects.filter(layout_id=pk).first()
        if not layout_info:
            return JsonResponse(R.build(msg="环境不存在"))
        try:
            desc = request.data['data']
            layout_info.layout_desc = desc
            layout_info.save()
        except:
            return JsonResponse(R.build(msg="编辑失败"))
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
                base_target_port = id + "-" + _port
                encode_base_target_port = base64.b64encode(base_target_port.encode("utf-8"))
                encode_base_target_port = "VULFOCUS" + encode_base_target_port.hex().upper()
                if encode_base_target_port not in env_list:
                    env_list.append(encode_base_target_port)
                port_str = "${" + encode_base_target_port + "}:" + _port + ""
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


def file_iterator(file_path, chunk_size=1024):
    with open(file_path, "rb") as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break



@api_view(http_method_names=["POST"])
def build_compose(request):
    '''
    构建docker-compose相关镜像
    '''
    user = request.user
    if not user.is_superuser:
        return JsonResponse(R.build(msg="权限不足"))
    user_id = user.id
    tag = request.data['tag']
    args = request.data['compose_content']
    try:
        args_yaml = yaml.load(args, Loader=yaml.FullLoader)
    except Exception as e:
        return JsonResponse({"code": 2001, "message": "格式错误"})
    local_images = [i.tags[0] for i in client.images.list() if i.tags]  # 本地所有镜像
    image_list = []
    env_list = []
    vul_port = []
    compose_env_port = []
    image_infos = ImageInfo.objects.filter(image_name=tag).first()
    user_info = UserProfile.objects.filter(id=user_id).first()
    data = request.data
    rank = 2.5
    degree = ''
    is_flag = True
    if 'is_flag' in data:
        is_flag = request.data['is_flag']
    if "rank" in data:
        rank = request.data['rank']
        if rank == 0:
            rank = 2.5
        rank = float(rank)
    if "degree" in data:
        degree = request.data['degree']
    if image_infos:
        return JsonResponse({"code": 2001, "message": "{}镜像已存在".format(tag)})
    if not tag:
        return JsonResponse({"code": 2001, "message": "镜像名称不能为空"})
    try:
        for services_name in args_yaml['services']:
            if "dockerfile" in args_yaml['services'][services_name]:
                return JsonResponse({"code": 2001, "message": "yml文件不允许自定义dockerfile"})
            if "container_name" in args_yaml['services'][services_name]:
                return JsonResponse({"code": 2001, "message": "yml文件不允许自定义容器名"})
            if "ports" in args_yaml['services'][services_name]:
                _ports = args_yaml['services'][services_name]['ports']
                yml_port_list = []
                for por in _ports:
                    port = por.split(':')[0]
                    ids = uuid.uuid4()
                    base_target_port = str(ids) + "-" + port
                    encode_base_target_port = base64.b64encode(base_target_port.encode("utf-8"))
                    encode_base_target_port = "VULFOCUS" + encode_base_target_port.hex().upper()
                    port_str = "${" + encode_base_target_port + "}:" + por.split(':')[1] + ""  # yml 端口
                    yml_port_list.append(port_str)
                    vul_port.append(por)
                    compose_env_port.append(port_str)
                    env_list.append(encode_base_target_port)
                args_yaml['services'][services_name]['ports'] = yml_port_list
        if ':' in tag:
            image_vul_name = tag.split(':')[0]
        else:
            image_vul_name = tag
        image_info = ImageInfo(image_name=tag, image_vul_name=image_vul_name, image_desc="", is_flag=is_flag,
                               rank=rank, degree=json.dumps(degree), is_ok=False, create_date=timezone.now()
                               , update_date=timezone.now(), is_docker_compose=True, docker_compose_yml=json.dumps(args_yaml)
                               , docker_compose_env=json.dumps(env_list), image_port=json.dumps(vul_port)
                               , compose_env_port=json.dumps(compose_env_port), original_yml=json.dumps(yaml.load(args,Loader=yaml.FullLoader)))

        image_info.save()
        image_list = tasks.create_compose_task(user_info, image_info, tag, get_request_ip(request))
    except Exception as e:
        return JsonResponse({"code": 2001, "message": "添加{}镜像构建任务失败".format(tag)})
    sys_log = SysLog(user_id=user_id, operation_type="镜像", operation_name="构建docker-compose", ip=get_request_ip(request),
                     operation_value=image_vul_name, operation_args="")
    sys_log.save()
    return JsonResponse({"code": 200, "message": "添加{}镜像构建任务成功".format(tag)})


@api_view(http_method_names=["POST"])
def update_build_compose(request):
    '''
    修改重新构建docker-compose相关镜像
    '''
    user = request.user
    if not user.is_superuser:
        return JsonResponse(R.build(msg="权限不足"))
    user_id = user.id
    image_id = request.data['image_id']
    args = request.data['compose_content']
    if not image_id:
        return JsonResponse({"code": 2001, "message": "错误的image_id"})
    try:
        args_yaml = yaml.load(args, Loader=yaml.FullLoader)
    except Exception as e:
        return JsonResponse({"code": 2001, "message": "格式错误"})
    image_infos = ImageInfo.objects.filter(image_id=image_id).first()
    user_info = UserProfile.objects.filter(id=user_id).first()
    if not image_infos:
        return JsonResponse({"code": 2001, "message": "镜像不存在"})
    env_list = []
    vul_port = []
    compose_env_port = []
    try:
        for services_name in args_yaml['services']:
            if "dockerfile" in args_yaml['services'][services_name]:
                return JsonResponse({"code": 2001, "message": "yml文件不允许自定义dockerfile"})
            if "container_name" in args_yaml['services'][services_name]:
                return JsonResponse({"code": 2001, "message": "yml文件不允许自定义容器名"})
            if "ports" in args_yaml['services'][services_name]:
                _ports = args_yaml['services'][services_name]['ports']
                yml_port_list = []
                for por in _ports:
                    port = por.split(':')[0]
                    ids = uuid.uuid4()
                    base_target_port = str(ids) + "-" + port
                    encode_base_target_port = base64.b64encode(base_target_port.encode("utf-8"))
                    encode_base_target_port = "VULFOCUS" + encode_base_target_port.hex().upper()
                    port_str = "${" + encode_base_target_port + "}:" + por.split(':')[1] + ""  # yml 端口
                    yml_port_list.append(port_str)
                    vul_port.append(por)
                    compose_env_port.append(port_str)
                    env_list.append(encode_base_target_port)
                args_yaml['services'][services_name]['ports'] = yml_port_list
        image_infos.is_ok = False
        image_infos.update_date = timezone.now()
        image_infos.docker_compose_yml = json.dumps(args_yaml)
        image_infos.docker_compose_env = json.dumps(env_list)
        image_infos.image_port = json.dumps(vul_port)
        image_infos.compose_env_port = json.dumps(compose_env_port)
        image_infos.original_yml = json.dumps(yaml.load(args, Loader=yaml.FullLoader))
        image_infos.save()
        tag = image_infos.image_name
        image_vul_name = image_infos.image_vul_name
        image_list = tasks.create_compose_task(user_info, image_infos, tag, get_request_ip(request))
    except Exception as e:
        return JsonResponse({"code": 2001, "message": "修改docker-compose镜像构建任务失败"})
    sys_log = SysLog(user_id=user_id, operation_type="镜像", operation_name="构建docker-compose", ip=get_request_ip(request),
                     operation_value=image_vul_name, operation_args="")
    sys_log.save()
    return JsonResponse({"code": 200, "message": "修改{}镜像构建任务成功".format(tag)})


@api_view(http_method_names=["GET"])
def show_compose(request):
    '''
    获取docker-compose构建状态
    '''
    user = request.user
    if not user.is_superuser:
        return JsonResponse(R.build(msg="权限不足"))
    user_id = user.id
    task_info = TaskInfo.objects.filter(operation_type=7, task_status=2, user_id=user_id).first()
    if task_info:
        data = json.loads(TaskSetSerializer(task_info).data['operation_args'])
        tag = data['tag']
        args_yaml = data['args_yaml']
        return JsonResponse({"code": 200, "message": "正在构建相关镜像", "data": args_yaml, "img_name": tag})
    else:
        return JsonResponse({"code": 202, "message": ""})


@api_view(http_method_names=["GET"])
def get_scene_data(request):
    '''
    获取场景
    '''
    tag = request.GET.get("tag", "all")
    page = request.GET.get("page", 1)
    query = request.GET.get("query", "")
    backstage = request.GET.get("backstage", "")
    user = request.user
    if backstage:
        if not user.is_superuser:
            return JsonResponse({"code": 200, "result": '权限不足'})
    if page:
        min_size = (int(page) - 1) * 20
        max_size = int(page) * 20
    else:
        min_size = 0
        max_size = 20
    all_list = []
    try:
        if tag == "hot" or tag == "all":
            if query:
                if backstage:
                    layout_data = Layout.objects.filter(Q(layout_name__contains=query) | Q(layout_desc__contains=query))
                else:
                    layout_data = Layout.objects.filter(Q(is_release=True), Q(layout_name__contains=query) | Q(layout_desc__contains=query))
            else:
                if backstage:
                    layout_data = Layout.objects.all()
                else:
                    layout_data = Layout.objects.filter(is_release=True)
            if layout_data:
                for lay in layout_data:
                    lay_dict = {}
                    user_count = LayoutServiceContainerScore.objects.filter(layout_id=lay).values('user_id').distinct().count()
                    lay_data = LayoutSerializer(lay).data
                    lay_dict['id'] = lay_data['layout_id']
                    lay_dict['name'] = lay_data['layout_name']
                    lay_dict['desc'] = lay_data['layout_desc']
                    lay_dict['image_name'] = lay_data['image_name']
                    lay_dict['is_release'] = lay_data['is_release']
                    lay_dict['is_uesful'] = lay_data['is_uesful']
                    lay_dict['status'] = lay_data['status']
                    lay_dict['type'] = "layoutScene"
                    lay_dict['user_count'] = user_count
                    # 场景点赞数
                    fav_num = SceneUserFav.objects.filter(scene_id=lay_dict['id']).count()
                    lay_dict["fav_num"] = fav_num
                    has_fav = SceneUserFav.objects.filter(scene_id=lay_dict['id'], user=request.user).exists()
                    lay_dict["have_fav"] = has_fav
                    lay_dict["total_view"] = lay_data['total_view']
                    lay_dict["download_num"] = lay_data["download_num"]
                    all_list.append(lay_dict)
            if query:
                temp_data = TimeTemp.objects.filter(Q(name__contains=query) | Q(time_desc__contains=query))
            else:
                temp_data = TimeTemp.objects.all()
            if temp_data:
                for temp in temp_data:
                    temp_dict = {}
                    user_count = TimeRank.objects.filter(time_temp=temp).count()
                    tem_data = TimeTempSerializer(temp).data
                    temp_dict['id'] = tem_data['temp_id']
                    temp_dict['name'] = tem_data['name']
                    temp_dict['desc'] = tem_data['time_desc']
                    temp_dict['image_name'] = tem_data['image_name']
                    temp_dict['type'] = "timeScene"
                    temp_dict['user_count'] = user_count
                    # 场景点赞数
                    fav_num = SceneUserFav.objects.filter(scene_id=temp_dict['id']).count()
                    temp_dict["fav_num"] = fav_num
                    has_fav = SceneUserFav.objects.filter(scene_id=temp_dict['id'], user=request.user).exists()
                    temp_dict["have_fav"] = has_fav
                    temp_dict["total_view"] = tem_data['total_view']
                    all_list.append(temp_dict)
            if tag == "hot":
                all_list = sorted(all_list, key=lambda keys: keys['user_count'],reverse=True)[min_size:max_size]
            else:
                all_list = all_list[min_size:max_size]
        elif tag == 'layout':
            if query:
                if backstage:
                    layout_data = Layout.objects.filter(Q(layout_name__contains=query) | Q(layout_desc__contains=query))
                else:
                    layout_data = Layout.objects.filter(Q(is_release=True),
                                                        Q(layout_name__contains=query) | Q(layout_desc__contains=query))
            else:
                if backstage:
                    layout_data = Layout.objects.all()
                else:
                    layout_data = Layout.objects.filter(is_release=True)
            if layout_data:
                for lay in layout_data:
                    lay_dict = {}
                    user_count = LayoutServiceContainerScore.objects.filter(layout_id=lay).values('user_id').distinct().count()
                    lay_data = LayoutSerializer(lay).data
                    lay_dict['id'] = lay_data['layout_id']
                    lay_dict['name'] = lay_data['layout_name']
                    lay_dict['desc'] = lay_data['layout_desc']
                    lay_dict['image_name'] = lay_data['image_name']
                    lay_dict['is_release'] = lay_data['is_release']
                    lay_dict['is_uesful'] = lay_data['is_uesful']
                    lay_dict['status'] = lay_data['status']
                    lay_dict['type'] = "layoutScene"
                    lay_dict['user_count'] = user_count
                    fav_num = SceneUserFav.objects.filter(scene_id=lay_dict['id']).count()
                    lay_dict["fav_num"] = fav_num
                    has_fav = SceneUserFav.objects.filter(scene_id=lay_dict['id'], user=request.user).exists()
                    lay_dict["have_fav"] = has_fav
                    lay_dict["total_view"] = lay_data['total_view']
                    lay_dict["download_num"] = lay_data["download_num"]
                    all_list.append(lay_dict)
            all_list = all_list[min_size:max_size]
        else:
            if query:
                temp_data = TimeTemp.objects.filter(Q(name__contains=query) | Q(time_desc__contains=query))
            else:
                temp_data = TimeTemp.objects.all()
            if temp_data:
                for temp in temp_data:
                    temp_dict = {}
                    user_count = TimeRank.objects.filter(time_temp=temp).count()
                    tem_data = TimeTempSerializer(temp).data
                    temp_dict['id'] = tem_data['temp_id']
                    temp_dict['name'] = tem_data['name']
                    temp_dict['desc'] = tem_data['time_desc']
                    temp_dict['image_name'] = tem_data['image_name']
                    temp_dict['type'] = "timeScene"
                    temp_dict['user_count'] = user_count
                    fav_num = SceneUserFav.objects.filter(scene_id=temp_dict['id']).count()
                    temp_dict["fav_num"] = fav_num
                    has_fav = SceneUserFav.objects.filter(scene_id=temp_dict['id'], user=request.user).exists()
                    temp_dict["have_fav"] = has_fav
                    temp_dict["total_view"] = tem_data['total_view']
                    all_list.append(temp_dict)
            all_list = all_list[min_size:max_size]
    except:
        return JsonResponse(R.err())
    count = len(all_list)
    return JsonResponse({"code": 200, "result": all_list, "count": count})


@api_view(http_method_names=["POST"])
def upload_zip_file(request):
    user = request.user
    if not user.is_superuser:
        return JsonResponse({"code": 400, "msg": "权限不足"})
    zip_file = request.data.get("zip_file", "")
    if not zip_file:
        return JsonResponse({"code": 400, "msg": "请上传文件"})
    file_name = zip_file.name
    try:
        if file_name.split(".")[-1] != "zip":
            return JsonResponse({"code": 400, "msg": "请上传zip格式的文件"})
        if not os.path.exists(UPLOAD_ZIP_PATH):
            os.makedirs(UPLOAD_ZIP_PATH)
    except Exception as e:
        return JsonResponse({"code": 400, "msg": "文件上传失败"})
    try:
        with open(os.path.join(UPLOAD_ZIP_PATH, file_name), "wb") as f:
            for chunk in zip_file.chunks():
                f.write(chunk)
    except Exception as e:
        return JsonResponse({"code": 400, "msg": "文件上传失败"})
    zf = zipfile.ZipFile(os.path.join(UPLOAD_ZIP_PATH, file_name))
    try:
        file_list = list(map(lambda file: file.replace(file_name.replace(".zip", "")+"/", ""), zf.namelist()))
    except Exception as e:
        return JsonResponse({"code": 400, "msg": "文件数据被修改，请重新上传"})
    # 判断压缩文件中文件数据是否丢失
    if "raw-content.json" not in file_list:
        return JsonResponse({"code": 400, "msg": "编排环境原数据丢失请重新上传"})
    if "layout_info.json" not in file_list:
        return JsonResponse({"code": 400, "msg": "编排环境相关信息数据丢失请重新上传"})
    flag = False
    layout_name, layout_desc, layout_image = "", "", ""
    for file in file_list:
        for suffix in ALLOWED_IMG_SUFFIX:
            if suffix in file:
                flag = True
                break
    if flag == False:
        return JsonResponse({"code": 400, "msg": "编排环境图片数据丢失请重新上传"})
    # 获取数据包中编排环境名称，编排环境描述,编排环境图片数据
    try:
        for file_name in zf.namelist():
            if "layout_info.json" in file_name:
                data = zf.read(file_name).decode("utf-8")
                layout_info = json.loads(data)
                layout_name = layout_info["layout_name"]
                layout_desc = layout_info["layout_desc"]
            elif file_name.split(".")[-1] in ALLOWED_IMG_SUFFIX:
                image_name = str(uuid.uuid4())
                image_data = zf.read(file_name)
                static_url = os.path.join(BASE_DIR, "static")
                if not os.path.exists(static_url):
                    os.makedirs(static_url)
                with open(os.path.join(static_url, "{image_name}.{suffix}".format(image_name=image_name,
                                                                                  suffix=file_name.split(".")[-1])),
                          "wb") as f:
                    f.write(image_data)
                layout_image = "{image_name}.{suffic}".format(image_name=image_name, suffic=file_name.split(".")[-1])
    except Exception as e:
        return JsonResponse({"code": 400, "msg": "文件上传失败"})
    try:
        for file_name in zf.namelist():
            if "layout_info.json" in file_name:
                data = zf.read(file_name).decode("utf-8")
                layout_info = json.loads(data)
                layout_name = layout_info["layout_name"]
                layout_desc = layout_info["layout_desc"]
            elif file_name.split(".")[-1] in ALLOWED_IMG_SUFFIX:
                image_name = str(uuid.uuid4())
                image_data = zf.read(file_name)
                static_url = os.path.join(BASE_DIR, "static")
                if not os.path.exists(static_url):
                    os.makedirs(static_url)
                with open(os.path.join(static_url, "{image_name}.{suffix}".format(image_name=image_name,
                                                                                  suffix=file_name.split(".")[-1])),
                          "wb") as f:
                    f.write(image_data)
                layout_image = "{image_name}.{suffic}".format(image_name=image_name, suffic=file_name.split(".")[-1])
    except Exception as e:
        return JsonResponse({"code": 400, "msg": "文件上传失败"})
    # 读取压缩包中原始编排环境信息
    for file_name in zf.namelist():
        if "raw-content.json" in file_name:
            try:
                data = zf.read(file_name).decode("utf8")
                raw_data = json.loads(data)
                if not raw_data:
                    return JsonResponse({"code": 400, "msg": "编排环境中数据为空"})
                nodes = raw_data["nodes"]
                if not nodes or len(nodes) == 0:
                    return JsonResponse({"code": 400, "msg": "编排环境中节点为空"})
                connectors = raw_data["connectors"]
                check_open = False
                container_list = []
                network_dict = {}
                check_network_name_list = []
                for node in nodes:
                    node_id = node["id"]
                    node_type = node["type"]
                    node_attrs = node["attrs"]
                    if len(node_attrs) == 0:
                        return JsonResponse({"code": 400, "msg": "编排环境中节点属性为空"})
                    if node_type == "Container":
                        node_open = node_attrs["open"]
                        node_port = node_attrs["port"]
                        if node_open and node_port:
                            check_open = True
                        if "is_docker_compose" in node["attrs"]['raw']:
                            if node["attrs"]['raw']["is_docker_compose"]:
                                return JsonResponse({"code": 400, "msg": "编排环境中镜像为docker-compose构建,不允许直接下载"})
                        image_name = node_attrs["name"]
                        image_desc = node_attrs["desc"]
                        image_vul_name = node_attrs["vul_name"]
                        image_port = node_attrs["port"]
                        rank = float(node_attrs["raw"]["rank"])
                        degree = node_attrs["raw"]["degree"]
                        image_info = ImageInfo.objects.filter(image_name=image_name).first()
                        if not image_info:
                            image_info = ImageInfo(image_id=str(uuid.uuid4()), image_name=image_name,
                                                   image_desc=image_desc,
                                                   image_port=image_port, image_vul_name=image_vul_name, rank=rank,
                                                   degree=degree, is_ok=False)
                            image_info.save()
                        container_list.append(node)
                    elif node_type == "Network":
                        network_name = node_attrs["name"]
                        subnet = node_attrs["subnet"]
                        gateway = node_attrs["gateway"]
                        net_work_scope = node_attrs["raw"]["net_work_scope"]
                        net_work_driver = node_attrs['raw']["net_work_driver"]
                        enable_ipv6 = node_attrs["raw"]["enable_ipv6"]
                        network_name_temp, subnet_temp, gateway_temp = "", "", ""
                        if not network_name:
                            return JsonResponse({"code": 400, "msg": "编排环境中网卡名称为空"})
                        if network_name in check_network_name_list:
                            return JsonResponse({"code": 400, "msg": "编排环境中重复设置了网卡"})
                        docker_networks = client.networks.list()
                        network_list = []
                        for single_network in docker_networks:
                            config_list = single_network.attrs['IPAM']['Config']
                            for single_config in config_list:
                                network_list.append(single_config["Gateway"].split(".")[0:2])
                            if single_network.name == network_name:
                                network_name_temp = network_name
                                network_name = str(uuid.uuid4())
                        current_subnet, current_gateway = subnet, gateway
                        # 统计网卡的遍历次数
                        count = 0
                        while gateway.split(".")[0:2] in network_list:
                            gateway_list = list(map(int, gateway.split(".")))
                            count += 1
                            if count >= 100:
                                return JsonResponse({"code": 400, "msg": "服务器内部网卡创建过多，请删除部分不需要网卡"})
                            if gateway_list[1] < 255:
                                gateway_list[1] += 1
                            else:
                                gateway_list[1] -= 1
                            gateway_temp = current_gateway
                            gateway_list = list(map(str, gateway_list))
                            gateway = ".".join(gateway_list)
                            subnet_temp = current_subnet
                            new_subnet_list = gateway.split(".")[0:2] + subnet.split(".")[2:]
                            subnet = ".".join(new_subnet_list)
                        try:
                            ipam_pool = docker.types.IPAMPool(subnet=subnet, gateway=gateway)
                            ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
                            try:
                                # 创建docker网卡之前需要判断是主机上否有同名网卡存在，有则移除
                                net_work = client.networks.create(network_name, driver=net_work_driver,
                                                                    ipam=ipam_config, scope=net_work_scope)
                            except Exception as e:
                                return JsonResponse({"code": 400, "msg": "编排环境中子网或者网关设置错误"})
                            net_work_client_id = str(net_work.id)
                            if not gateway:
                                gateway = net_work.attrs['IPAM']['Config']['Gateway']
                            created_network = NetWorkInfo(net_work_id=str(uuid.uuid4()),
                                                            net_work_client_id=net_work_client_id,
                                                            create_user=user.id,
                                                            net_work_name=network_name,
                                                            net_work_driver=net_work_driver,
                                                            net_work_subnet=subnet,
                                                            net_work_gateway=gateway, net_work_scope=net_work_scope,
                                                            enable_ipv6=enable_ipv6)
                            created_network.save()
                        except Exception as e:
                            return JsonResponse({"code": 400, "msg": "服务器内部错误"})
                        check_network_name_list.append(network_name)
                        network_dict[node_id] = node
                        str_network_dict = json.dumps(network_dict)
                        str_check_network_name_list = json.dumps(check_network_name_list)
                        str_raw_data = json.dumps(raw_data)
                        if network_name_temp and network_name_temp != "":
                            str_check_network_name_list = str_check_network_name_list.replace(json.dumps(network_name_temp),
                                                                                              '"{}"'.format(network_name))
                            str_network_dict = str_network_dict.replace(json.dumps(network_name_temp), '"{}"'.format(network_name))
                            str_raw_data = str_raw_data.replace(json.dumps(network_name_temp), '"{}"'.format(network_name))
                        if subnet_temp and subnet_temp != "":
                            str_network_dict = str_network_dict.replace(subnet_temp, subnet)
                            str_raw_data = str_raw_data.replace(subnet_temp, subnet)
                        if gateway_temp and gateway_temp != "":
                            str_network_dict = str_network_dict.replace(gateway_temp, gateway)
                            str_raw_data = str_raw_data.replace(gateway_temp, gateway)
                        network_dict = json.loads(str_network_dict)
                        check_network_name_list = json.loads(str_check_network_name_list)
                        raw_data = json.loads(str_raw_data)
                if not check_open:
                    return JsonResponse({"code": 400, "msg": "编排环境中未开放访问路口"})
                if len(container_list) == 0:
                    return JsonResponse({"code": 400, "msg": "编排环境中容器为空"})
                if len(network_dict) == 0:
                    for container in container_list:
                        if not container["attrs"]["open"]:
                            return JsonResponse({"code": 400, "msg": "编排环境中未配置网卡且未开放访问路口"})
                else:
                    if not connectors or len(connectors) == 0:
                        return JsonResponse({"code": 400, "msg": "编排环境中连接点为空"})
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
                        layout_instance = Layout.objects.filter(layout_name=layout_name,
                                                                layout_desc=layout_desc).first()
                        if layout_instance:
                            operation_name = "修改"
                            return JsonResponse({"code": 400, "msg": "已经有同名编排环境存在"})
                        else:
                            layout_instance = Layout(layout_id=str(uuid.uuid4()), create_date=timezone.now(),
                                                     update_date=timezone.now(), is_uesful=False)
                        layout_data = LayoutData.objects.filter(layout_id=layout_instance).first()
                        if layout_data and layout_data.status == "running":
                            return JsonResponse({"code": 400, "msg": "环境正在运行中，请先停止相关环境"})
                        layout_instance.layout_name = layout_name
                        layout_instance.layout_desc = layout_desc
                        layout_instance.create_user_id = user.id
                        layout_instance.image_name = layout_image
                        layout_instance.raw_content = json.dumps(raw_data, ensure_ascii=False)
                        layout_instance.yml_content = yaml.dump(yml_content["content"])
                        layout_instance.env_content = env_content
                        layout_instance.save()
                        # 修改相关编排环境的相关服务信息
                        layout_service_list = list(
                            LayoutService.objects.filter(layout_id=layout_instance).values("service_id"))
                        services = yml_data["services"]
                        for service_name in services:
                            service = services[service_name]
                            image = service["image"]
                            image_info = ImageInfo.objects.filter(image_name=image).first()
                            is_exposed = False
                            ports = ""
                            if "ports" in service and len(service["ports"]) > 0:
                                is_exposed = True
                            if image_info.image_port:
                                ports = ",".join(str(image_info.image_port).split(","))
                            layout_service = LayoutService.objects.filter(layout_id=layout_instance,
                                                                          service_name=service_name).first()
                            if not layout_service:
                                layout_service = LayoutService(service_id=str(uuid.uuid4()), layout_id=layout_instance,
                                                               service_name=service_name,
                                                               create_date=timezone.now(), update_date=timezone.now())
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
                                service_network = LayoutServiceNetwork.objects.filter(service_id=layout_service,
                                                                                      network_id=network_info).first()
                                if not service_network:
                                    service_network = LayoutServiceNetwork(layout_service_network_id=str(uuid.uuid4()),
                                                                           service_id=layout_service,
                                                                           network_id=network_info,
                                                                           create_date=timezone.now(),
                                                                           update_date=timezone.now())
                                if {
                                    "layout_service_network_id": service_network.layout_service_network_id} in service_network_list:
                                    service_network_list.remove({"layout_service_network_id": service_network.
                                                                layout_service_network_id})
                                service_network.save()
                            #  删除不存在的网卡
                            try:
                                if len(service_network_list) > 0:
                                    for service_network in service_network_list:
                                        LayoutServiceNetwork.objects.filter(layout_service_network_id=
                                                                            service_network[
                                                                                "layout_service_network_id"]).delete()
                            except:
                                pass
                        # 删除服务数据
                        for layout_service in layout_service_list:
                            service_id = layout_service['service_id']
                            LayoutService.objects.filter(service_id=service_id, layout_id=layout_instance).delete()
                            if layout_data:
                                LayoutServiceContainer.objects.filter(service_id=service_id,
                                                                      layout_user_id=layout_data).delete()
                                LayoutServiceContainerScore.objects.filter(layout_id=layout_instance,
                                                                           layout_data_id=layout_data,
                                                                           service_id=service_id).delete()
                            else:
                                LayoutServiceContainer.objects.filter(service_id=service_id).delete()
                                LayoutServiceContainerScore.objects.filter(layout_id=layout_instance,
                                                                           service_id=service_id).delete()
                except Exception as e:
                    return JsonResponse({"code": 400, "msg": "服务器内部错误"})
            except Exception as e:
                return JsonResponse({"code": 400, "msg": "文件上传失败"})
        else:
            continue
    return JsonResponse({"code": 200, "msg": "上传成功", 'layout_id': layout_instance.layout_id})


@api_view(http_method_names=["POST"])
def download_layout_image(request):
    user = request.user
    if not user.is_superuser:
        return JsonResponse({"status": 400, "msg": "权限不足"})
    layout_image_id = request.data.get("layout_image_id", "")
    if not layout_image_id:
        return JsonResponse({"status": 400, "msg": "编排环境id不能为空"})
    layout_instance = Layout.objects.filter(layout_id=layout_image_id).first()
    if not layout_instance:
        return JsonResponse({"status": 400, "msg": "不存在该编排环境"})
    yml_data = yaml.load(layout_instance.yml_content, Loader=yaml.Loader)
    services = yml_data["services"]
    try:
        for service in services:
            image_name = services[service]["image"]
            image_info = ImageInfo.objects.filter(image_name=image_name).first()
            if not image_info:
                image_vul_name = image_name[:image_name.rfind(":")]
                image_info = ImageInfo(image_name=image_name, image_vul_name=image_vul_name, image_desc=image_vul_name,
                                       rank=2.5, is_ok=False, create_date=timezone.now(), update_date=timezone.now())
                image_info.save()
        tasks.create_layout_image_download_task(layout_instance, user)
        return JsonResponse({"code": 200, "msg": "开始下载"})
    except Exception as e:
        return JsonResponse({"code": 400, "msg": "服务器内部错误"})


@api_view(http_method_names=["POST"])
def download_official_website_layout(request):
    '''
    下载官网编排场景（社区）
    '''
    data = request.data
    id = data['layout_id']    # 真实官网id
    user = request.user
    url = "http://vulfocus.fofa.so/api/layoutinfodet?layout_id={}".format(id)
    res = requests.get(url, verify=False).content
    req = json.loads(res)
    raw_data = req['data']['layout_raw_content']
    raw_data = yaml.load(raw_data, Loader=yaml.Loader)
    static_url = os.path.join(BASE_DIR, "static")
    img_url = req['data']['image_name']   # 官网图片
    con = requests.get(img_url, verify=False).content  # 下载官网图片写入文件夹
    imagename = str(uuid.uuid4())   # 图片名称随机uuid
    if not os.path.exists(static_url):
        os.makedirs(static_url)
    with open(os.path.join(static_url, "{image_name}.png".format(image_name=imagename)), "wb") as f:
        f.write(con)
    layout_image = "{image_name}.png".format(image_name=imagename)
    if not raw_data:
        return JsonResponse({"code": 400, "msg": "编排环境中数据为空"})
    nodes = raw_data["nodes"]
    if not nodes or len(nodes) == 0:
        return JsonResponse({"code": 400, "msg": "编排环境中节点为空"})
    connectors = raw_data["connectors"]
    check_open = False
    container_list = []
    network_dict = {}
    check_network_name_list = []
    for node in nodes:
        node_id = node["id"]
        node_type = node["type"]
        node_attrs = node["attrs"]
        if len(node_attrs) == 0:
            return JsonResponse({"code": 400, "msg": "编排环境中节点属性为空"})
        if node_type == "Container":
            node_open = node_attrs["open"]
            node_port = node_attrs["port"]
            if node_open and node_port:
                check_open = True
            if "is_docker_compose" in node["attrs"]['raw']:
                if node["attrs"]['raw']["is_docker_compose"]:
                    return JsonResponse({"code": 400, "msg": "编排环境中镜像为docker-compose构建,不允许直接下载"})
            image_name = node_attrs["name"]
            image_desc = node_attrs["desc"]
            image_vul_name = node_attrs["vul_name"]
            image_port = node_attrs["port"]
            rank = float(node_attrs["raw"]["rank"])
            degree = node_attrs["raw"]["degree"]
            image_info = ImageInfo.objects.filter(image_name=image_name).first()
            if not image_info:
                image_info = ImageInfo(image_id=str(uuid.uuid4()), image_name=image_name, image_desc=image_desc,
                                       image_port=image_port, image_vul_name=image_vul_name, rank=rank,
                                       degree=degree, is_ok=False)
                image_info.save()
            container_list.append(node)
        elif node_type == "Network":
            network_name = node_attrs["name"]
            subnet = node_attrs["subnet"]
            gateway = node_attrs["gateway"]
            net_work_scope = node_attrs["raw"]["net_work_scope"]
            net_work_driver = node_attrs['raw']["net_work_driver"]
            enable_ipv6 = node_attrs["raw"]["enable_ipv6"]
            network_name_temp, subnet_temp, gateway_temp = "", "", ""
            if not network_name:
                return JsonResponse({"code": 400, "msg": "编排环境中网卡名称为空"})
            if network_name in check_network_name_list:
                return JsonResponse({"code": 400, "msg": "编排环境中重复设置了网卡"})
            docker_networks = client.networks.list()
            network_list = []
            for single_network in docker_networks:
                config_list = single_network.attrs['IPAM']['Config']
                for single_config in config_list:
                    network_list.append(single_config["Gateway"].split(".")[0:2])
                if single_network.name == network_name:
                    network_name_temp = network_name
                    network_name = str(uuid.uuid4())
            current_subnet, current_gateway = subnet, gateway
            # 统计网卡的遍历次数
            count = 0
            while gateway.split(".")[0:2] in network_list:
                gateway_list = list(map(int, gateway.split(".")))
                count += 1
                if count >= 100:
                    return JsonResponse({"code": 400, "msg": "服务器内部网卡创建过多，请删除部分不需要网卡"})
                if gateway_list[1] < 255:
                    gateway_list[1] += 1
                else:
                    gateway_list[1] -= 1
                gateway_temp = current_gateway
                gateway_list = list(map(str, gateway_list))
                gateway = ".".join(gateway_list)
                subnet_temp = current_subnet
                new_subnet_list = gateway.split(".")[0:2] + subnet.split(".")[2:]
                subnet = ".".join(new_subnet_list)
            try:
                ipam_pool = docker.types.IPAMPool(subnet=subnet, gateway=gateway)
                ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
                try:
                    # 创建docker网卡之前需要判断是主机上否有同名网卡存在，有则移除
                    net_work = client.networks.create(network_name, driver=net_work_driver,
                                                      ipam=ipam_config, scope=net_work_scope)
                except Exception as e:
                    return JsonResponse({"code": 400, "msg": "编排环境中子网或者网关设置错误"})
                net_work_client_id = str(net_work.id)
                if not gateway:
                    gateway = net_work.attrs['IPAM']['Config']['Gateway']
                created_network = NetWorkInfo(net_work_id=str(uuid.uuid4()),
                                              net_work_client_id=net_work_client_id,
                                              create_user=user.id,
                                              net_work_name=network_name,
                                              net_work_driver=net_work_driver,
                                              net_work_subnet=subnet,
                                              net_work_gateway=gateway, net_work_scope=net_work_scope,
                                              enable_ipv6=enable_ipv6)
                created_network.save()
            except Exception as e:
                return JsonResponse({"code": 400, "msg": "服务器内部错误"})
            check_network_name_list.append(network_name)
            network_dict[node_id] = node
            str_network_dict = json.dumps(network_dict)
            str_check_network_name_list = json.dumps(check_network_name_list)
            str_raw_data = json.dumps(raw_data)
            if network_name_temp and network_name_temp != "":
                str_check_network_name_list = str_check_network_name_list.replace(json.dumps(network_name_temp),
                                                                                  '"{}"'.format(network_name))
                str_network_dict = str_network_dict.replace(json.dumps(network_name_temp), '"{}"'.format(network_name))
                str_raw_data = str_raw_data.replace(json.dumps(network_name_temp), '"{}"'.format(network_name))
            if subnet_temp and subnet_temp != "":
                str_network_dict = str_network_dict.replace(subnet_temp, subnet)
                str_raw_data = str_raw_data.replace(subnet_temp, subnet)
            if gateway_temp and gateway_temp != "":
                str_network_dict = str_network_dict.replace(gateway_temp, gateway)
                str_raw_data = str_raw_data.replace(gateway_temp, gateway)
            network_dict = json.loads(str_network_dict)
            check_network_name_list = json.loads(str_check_network_name_list)
            raw_data = json.loads(str_raw_data)
    if not check_open:
        return JsonResponse({"code": 400, "msg": "编排环境中未开放访问路口"})
    if len(container_list) == 0:
        return JsonResponse({"code": 400, "msg": "编排环境中容器为空"})
    if len(network_dict) == 0:
        for container in container_list:
            if not container["attrs"]["open"]:
                return JsonResponse({"code": 400, "msg": "编排环境中未配置网卡且未开放访问路口"})
    else:
        if not connectors or len(connectors) == 0:
            return JsonResponse({"code": 400, "msg": "编排环境中连接点为空"})
    try:
        yml_content = build_yml(container_list=container_list, network_dict=network_dict, connector_list=connectors)
        yml_data = yml_content["content"]
        env_data = yml_content["env"]
        env_content = ""
        if len(env_data) > 0:
            env_content = "\n".join(env_data)
        with transaction.atomic():
            operation_name = "创建"
            layout_instance = Layout.objects.filter(layout_name=req['data']['layout_name'], layout_desc=req['data']['layout_desc']).first()
            if layout_instance:
                operation_name = "修改"
                return JsonResponse({"code": 400, "msg": "已经有同名编排环境存在"})
            else:
                layout_instance = Layout(layout_id=str(uuid.uuid4()), create_date=timezone.now(),
                                         update_date=timezone.now(), is_uesful=False)
            layout_data = LayoutData.objects.filter(layout_id=layout_instance).first()
            if layout_data and layout_data.status == "running":
                return JsonResponse({"code": 400, "msg": "环境正在运行中，请先停止相关环境"})
            layout_instance.layout_name = req['data']['layout_name']
            layout_instance.layout_desc = req['data']['layout_desc']
            layout_instance.create_user_id = user.id
            layout_instance.image_name = layout_image
            layout_instance.raw_content = json.dumps(raw_data, ensure_ascii=False)
            layout_instance.yml_content = yaml.dump(yml_content["content"])
            layout_instance.env_content = env_content
            layout_instance.save()
            # 修改相关编排环境的相关服务信息
            layout_service_list = list(LayoutService.objects.filter(layout_id=layout_instance).values("service_id"))
            services = yml_data["services"]
            for service_name in services:
                service = services[service_name]
                image = service["image"]
                image_info = ImageInfo.objects.filter(image_name=image).first()
                is_exposed = False
                ports = ""
                if "ports" in service and len(service["ports"]) > 0:
                    is_exposed = True
                if image_info.image_port:
                    ports = ",".join(str(image_info.image_port).split(","))
                layout_service = LayoutService.objects.filter(layout_id=layout_instance,
                                                              service_name=service_name).first()
                if not layout_service:
                    layout_service = LayoutService(service_id=str(uuid.uuid4()), layout_id=layout_instance,
                                                   service_name=service_name,
                                                   create_date=timezone.now(), update_date=timezone.now())
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
                    service_network = LayoutServiceNetwork.objects.filter(service_id=layout_service,
                                                                          network_id=network_info).first()
                    if not service_network:
                        service_network = LayoutServiceNetwork(layout_service_network_id=str(uuid.uuid4()),
                                                               service_id=layout_service,
                                                               network_id=network_info,
                                                               create_date=timezone.now(),
                                                               update_date=timezone.now())
                    if {"layout_service_network_id": service_network.layout_service_network_id} in service_network_list:
                        service_network_list.remove({"layout_service_network_id": service_network.
                                                    layout_service_network_id})
                    service_network.save()
                #  删除不存在的网卡
                if len(service_network_list) > 0:
                    for service_network in service_network_list:
                        LayoutServiceNetwork.objects.filter(layout_service_network_id=
                                                            service_network[
                                                                "layout_service_network_id"]).delete()
            # 删除服务数据
            for layout_service in layout_service_list:
                service_id = layout_service['service_id']
                LayoutService.objects.filter(service_id=service_id, layout_id=layout_instance).delete()
                if layout_data:
                    LayoutServiceContainer.objects.filter(service_id=service_id, layout_user_id=layout_data).delete()
                    LayoutServiceContainerScore.objects.filter(layout_id=layout_instance, layout_data_id=layout_data,
                                                               service_id=service_id).delete()
                else:
                    LayoutServiceContainer.objects.filter(service_id=service_id).delete()
                    LayoutServiceContainerScore.objects.filter(layout_id=layout_instance,
                                                               service_id=service_id).delete()
    except Exception as e:
        return JsonResponse({"code": 400, "msg": "服务器内部错误"})
    return JsonResponse({'code': 200, 'msg': '下载完成'})

@api_view(http_method_names=["GET"])
def get_official_website_layout(request):
    '''
    获取官网编排场景信息（社区）
    '''
    url = "http://vulfocus.fofa.so/api/get/layoutinfo/"
    try:
        res = requests.get(url, verify=False).content
        req = json.loads(res)
        if req and 'data' in req:
            if req['data']:
                data = req['data']
            else:
                data = []
        else:
            data = []
    except:
        data = []
    return JsonResponse(R.ok(data))


@api_view(http_method_names=["POST"])
def thumbUp(request):
    """
    场景点赞
    :param request:
    :return:
    """
    user = request.user
    scene_id = request.data.get("scene_id", "")
    scene_fav = SceneUserFav.objects.filter(user=user, scene_id=scene_id).first()
    if not scene_fav:
        new_scene_fav = SceneUserFav()
        new_scene_fav.user = user
        new_scene_fav.scene_id = scene_id
        new_scene_fav.save()
    else:
        scene_fav.delete()
    return JsonResponse(R.ok())
