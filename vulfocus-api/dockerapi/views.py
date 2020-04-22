import uuid, time, random, socket, traceback
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from dockerapi.models import ImageInfo
from dockerapi.serializers import ImageInfoSerializer, ContainerVulSerializer, SysLogSerializer
from dockerapi.models import ContainerVul
from vulfocus.settings import client, VUL_IP
import django.utils
import django.utils.timezone as timezone
from docker.errors import NotFound, ImageNotFound
from .common import R
from django.db.models import Q
from docker.models.images import Image
from .models import SysLog


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
        if query:
            query = query.strip()
            image_info_list = ImageInfo.objects.filter(Q(image_name__contains=query) | Q(image_vul_name__contains=query)
                                                       | Q(image_desc__contains=query))
        else:
            image_info_list = ImageInfo.objects.all()
        return image_info_list

    def destroy(self, request, *args, **kwargs):
        """
        删除镜像
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user = request.user
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足"))
        img = self.get_object()

        operation_args = ImageInfoSerializer(img).data
        request_ip = get_request_ip(request)
        sys_log = SysLog(user_id=user.id, operation_type="镜像", operation_name="删除",
                         operation_value=operation_args["image_vul_name"], operation_args=operation_args, ip=request_ip)
        sys_log.save()

        image_id = img.image_id
        container_vul = ContainerVul.objects.filter(image_id=image_id)
        if container_vul.count() == 0:
            img.delete()
            return JsonResponse(R.ok())
        else:
            return JsonResponse(R.build(msg="镜像正在使用，无法删除！"))

    def create(self, request, *args, **kwargs):
        """
        创建镜像
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user = request.user
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足！"))
        file = request.FILES.get("file")
        rank = request.POST.get("rank", default=2.5)
        image_name = request.POST.get("name")
        try:
            rank = float(rank)
        except Exception as e:
            return JsonResponse(R.build(msg="Rank 格式错误"))
        image_vul_name = request.POST.get("vul_name", default="")
        if not image_vul_name:
            return JsonResponse(R.build(msg="漏洞名称不能为空"))
        image_desc = request.POST.get("desc", default="")
        if not file and not image_name:
            return JsonResponse(R.build(msg="镜像文件或名称不能为空"))
        if file and image_name:
            return JsonResponse(R.build(msg="镜像文件或名称不能同时填写"))
        image_port = ""
        if not image_name and file:
            try:
                file_info = file.read()
                images = client.images.load(file_info)
                image = images[0]
                repo_tags = image.attrs["RepoTags"]
                if len(repo_tags) == 0:
                    # 移除本地镜像
                    try:
                        client.images.remove(image.id)
                    except Exception as e:
                        pass
                    return JsonResponse(msg="镜像名称不能为空")
                config = image.attrs["ContainerConfig"]
                port_list = []
                if "ExposedPorts" in config:
                    port_list = config["ExposedPorts"]
                ports = []
                for port in port_list:
                    port = port.replace("/", "").replace("tcp", "").replace("udp", "")
                    ports.append(port)
                image_name = repo_tags[0]
                image_port = ",".join(ports)
            except Exception as e:
                return JsonResponse(R.err())
        """
        查重
        """
        count = ImageInfo.objects.filter(image_name=image_name).count()
        if count > 0:
            return JsonResponse(R.build(msg="漏洞镜像已存在!"))
        if not file and image_name:
            try:
                image = client.images.get(image_name)
            except Exception as e:
                images = client.images.pull(image_name)
                if Image == type(images):
                    image = images
                else:
                    if len(images) > 0:
                        image = images[0]
                    else:
                        return JsonResponse(R.build("镜像不存在！"))
            config = image.attrs["ContainerConfig"]
            port_list = []
            if "ExposedPorts" in config:
                port_list = config["ExposedPorts"]
            ports = []
            for port in port_list:
                port = port.replace("/", "").replace("tcp", "").replace("udp", "")
                ports.append(port)
            image_port = ",".join(ports)
        image_info = ImageInfo(image_name=image_name, image_vul_name=image_vul_name, image_port=image_port, rank=rank,
                               image_desc=image_desc)
        image_info.save()
        rs_data = ImageInfoSerializer(image_info).data

        request_ip = get_request_ip(request)
        sys_log = SysLog(user_id=user.id, operation_type="镜像", operation_name="创建",
                         operation_value=rs_data["image_vul_name"], operation_args=rs_data, ip=request_ip)
        sys_log.save()
        return JsonResponse(R.ok(data=rs_data))

    @action(methods=["post", "get"], detail=True, url_path="start")
    def start_container(self, request, pk=None):
        """
        启动靶场
        :param request:
        :param pk:
        :return:
        """
        Img = self.get_object()
        # 当前用户登录ID
        user_id = request.user.id
        image_id = Img.image_id
        time_model_id = ''
        try:
            container_vul = ContainerVul.objects.filter(user_id=user_id, image_id=image_id, time_model_id=time_model_id).first()
            # 连接Docker容器
            docker_container = client.containers.get(container_id=container_vul.docker_container_id)
            # 当前状态
            if 'exited' == container_vul.container_status or 'exited' == docker_container.status:
                # 启动
                docker_container.start()
                time_sleep_count = 10
                container_status = str(docker_container.status)
                for i in range(time_sleep_count):
                    docker_container.reload()
                    container_status = str(docker_container.status)
                    if 'running' == container_status:
                        break
                    elif 'exited' == container_status:
                        pass
                    time.sleep(1)
                if 'running' != container_status:
                    return JsonResponse({"info": "", "msg": "漏洞容器启动失败"}, status=202)
                container_vul.container_status = container_status
                container_vul.save()

                operation_args = ImageInfoSerializer(Img).data
                request_ip = get_request_ip(request)
                sys_log = SysLog(user_id=user_id, operation_type="镜像", operation_name="启动",
                                 operation_value=operation_args["image_vul_name"], operation_args=operation_args,
                                 ip=request_ip)
                sys_log.save()

            return JsonResponse({"info": container_vul.vul_host, "container_id": container_vul.container_id, "msg": "容器已启动"},status=201)
        except AttributeError as attribute_error:
            pass
        except NotFound as docker_not_found:
            # 容器不存在，直接删除数据库记录
            container_vul.delete()
        except Exception as e:
            return JsonResponse({"info": "", "msg": "服务器内部错误，请联系管理员"}, status=500)
        vul_flag = "flag-{bmh%s}" % (uuid.uuid4(),)
        vul_ip = get_local_ip()
        if not vul_ip:
            return JsonResponse({"info": "", "msg": "服务器内部错误，请联系管理员"}, status=500)
        command = 'touch /tmp/%s' % (vul_flag, )
        image_port = Img.image_port
        image_port_list = image_port.split(',')
        port_dict = {}
        for tmp_port in image_port_list:
            tmp_random_port = ''
            for i in range(20):
                try:
                    # 端口
                    tmp_random_port = random.randint(8000, 65536)
                    ContainerVul.objects.get(container_port=tmp_random_port)
                    print('端口重复 --> %s' % (tmp_random_port,))
                except Exception as e:
                    break
            if not tmp_random_port:
                return JsonResponse({"info": "", "msg": "端口无效"}, status=202)
            port_dict['%s/tcp' % (tmp_port, )] = tmp_random_port
        try:
            container = client.containers.run(image=Img.image_name, ports=port_dict, detach=True)
            time_sleep_count = 10
            container_status = str(container.status)
            for i in range(time_sleep_count):
                container.reload()
                container_status = str(container.status)
                if 'running' == container_status:
                    print(container.exec_run(command))
                    break
                elif 'exited' == container_status:
                    break
                time.sleep(1)
            # docker 容器 id
            docker_container_id = container.id
            port_list = port_dict.values()
            tmp_port_list = []
            for tmp_port in port_list:
                tmp_port_list.append(str(tmp_port))
            port_str = ",".join(tmp_port_list)
            vul_host = vul_ip + ':' + port_str
            container_vul = ContainerVul(image_id=Img, user_id=request.user.id, vul_host=vul_host,
                                         container_status=container_status,
                                         docker_container_id=docker_container_id,
                                         container_port=port_str,
                                         time_model_id=time_model_id,
                                         create_date=django.utils.timezone.now(),
                                         container_flag=vul_flag)
            container_vul.save()

            operation_args = ImageInfoSerializer(Img).data
            request_ip = get_request_ip(request)
            sys_log = SysLog(user_id=user_id, operation_type="镜像", operation_name="启动",
                             operation_value=operation_args["image_vul_name"], operation_args=operation_args, ip=request_ip)
            sys_log.save()

            return JsonResponse({"info": vul_host, "container_id": container_vul.container_id}, status=201)
        except ImageNotFound as image_not_found:
            return JsonResponse({"info": "", "msg": "镜像不存在"})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"info": "", "msg": "服务器内部错误，请联系管理员"}, status=500)


class ContainerVulViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = ContainerVulSerializer

    def get_queryset(self):
        request = self.request
        user = request.user
        flag = request.GET.get("flag", "")
        if flag == 'list' and user.is_superuser:
            container_vul_list = ContainerVul.objects.all()
        else:
            container_vul_list = ContainerVul.objects.all().filter(user_id=self.request.user.id, time_model_id="")
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
        user_id = user_info.id

        operation_args = ContainerVulSerializer(container_vul).data
        request_ip = get_request_ip(request)
        sys_log = SysLog(user_id=user_id, operation_type="镜像", operation_name="启动",
                         operation_value=operation_args["vul_name"], operation_args=operation_args,
                         ip=request_ip)
        sys_log.save()

        if user_info.is_superuser or user_id == container_vul.user_id:
            try:
                # docker 连接容器ID
                docker_container_id = container_vul.docker_container_id
                # 连接Docker容器
                docker_container = client.containers.get(docker_container_id)
                docker_container.start()
                container_vul.container_status = 'running'
                container_vul.save()
                return JsonResponse({"info": container_vul.vul_host, "container_id": container_vul.container_id}, status=201)
            except Exception as e:
                return JsonResponse({"msg": "服务器内部错误", "code": "500"}, status=500)
        else:
            return JsonResponse({"msg": "权限不足", "code": "202"})

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
        user_id = user_info.id

        operation_args = ContainerVulSerializer(container_vul).data
        request_ip = get_request_ip(request)
        sys_log = SysLog(user_id=user_id, operation_type="镜像", operation_name="停止",
                         operation_value=operation_args["vul_name"], operation_args=operation_args,
                         ip=request_ip)
        sys_log.save()

        if user_info.is_superuser or user_id == container_vul.user_id:
            try:
                # docker 连接容器ID
                docker_container_id = container_vul.docker_container_id
                # 连接 Docker 容器
                docker_container = client.containers.get(docker_container_id)
                docker_container.stop()
                container_vul.container_status = 'stop'
                container_vul.save()
                return JsonResponse({"msg": "停止成功", "code": "202"}, status=201)
            except NotFound as not_found:
                container_vul.delete()
                return JsonResponse({"msg": "停止成功", "code": "202"}, status=201)
            except Exception as e:
                return JsonResponse({"msg": "停止失败，服务器内部错误", "code": "500"}, status=500)
        else:
            return JsonResponse({"msg": "权限不足", "code": "202"})

    '''
    删除容器
    '''
    @action(methods=["delete"], detail=True, url_path="delete")
    def delete_container(self, request, pk=None):
        user_info = request.user
        container_vul = self.get_object()
        user_id = user_info.id

        operation_args = ContainerVulSerializer(container_vul).data
        request_ip = get_request_ip(request)
        sys_log = SysLog(user_id=user_id, operation_type="镜像", operation_name="删除",
                         operation_value=operation_args["vul_name"], operation_args=operation_args,
                         ip=request_ip)
        sys_log.save()
        if user_info.is_superuser or user_id == container_vul.user_id:
            # docker 连接容器ID
            docker_container_id = container_vul.docker_container_id
            try:
                # 连接Docker容器
                docker_container = client.containers.get(docker_container_id)
                # 停止容器运行
                docker_container.stop()
                # 删除容器
                docker_container.remove()
            except Exception as e:
                print(e)
            # 删除对象
            container_vul.delete()
            return JsonResponse({"msg": "删除成功", "code": "201"}, status=201)
        else:
            return JsonResponse({"msg": "权限不足", "code": "202"})

    '''
    验证Flag是否正确
    '''
    @action(methods=["post", "get"], detail=True, url_path="flag")
    def check_flag(self, request, pk=None):
        flag = request.GET.get('flag', None)
        container_vul = self.get_object()
        user_id = request.user.id

        operation_args = ContainerVulSerializer(container_vul).data
        request_ip = get_request_ip(request)
        sys_log = SysLog(user_id=user_id, operation_type="镜像", operation_name="提交Flag",
                         operation_value=operation_args["vul_name"], operation_args={"flag": flag},
                         ip=request_ip)
        sys_log.save()

        if user_id != container_vul.user_id:
            return JsonResponse({"code": "2003", "msg": "与用户不匹配"})
        if not flag:
            return JsonResponse({"code": "2003", "msg": "Flag不能为空"})
        try:
            if flag != container_vul.container_flag:
                return JsonResponse({"code": "2001", "msg": "flag错误"})
            else:
                if not container_vul.is_check:
                    # 更新为通过
                    container_vul.is_check_date = django.utils.timezone.now()
                    container_vul.is_check = True
                    try:
                        docker_container_id = container_vul.docker_container_id
                        docker_container = client.containers.get(container_id=docker_container_id)
                        docker_container.stop()
                        container_vul.container_status = 'stop'
                        container_vul.save()
                    except Exception as e:
                        pass
                return JsonResponse({"code": "2000", "msg": "OK"}, status=201)
        except Exception as e:
            return JsonResponse({"code": "2002", "msg": str(e)})

    '''
    获取靶场状态信息
    '''
    @action(methods=["get"], detail=True, url_path="status")
    def status_container(self, request, pk=None):
        container_vul = self.get_object()
        user_id = request.user.id

        operation_args = ContainerVulSerializer(container_vul).data
        request_ip = get_request_ip(request)
        sys_log = SysLog(user_id=user_id, operation_type="镜像", operation_name="状态",
                         operation_value=operation_args["vul_name"], operation_args=operation_args,
                         ip=request_ip)
        sys_log.save()

        if container_vul.user_id != user_id:
            return JsonResponse({"code": "2003", "msg": "与用户不匹配"})
        info = ContainerVulSerializer(container_vul)
        rs_data = info.data
        return JsonResponse(rs_data)


class SysLogSet(viewsets.ModelViewSet):

    serializer_class = SysLogSerializer

    def get_queryset(self):
        request = self.request
        user = request.user
        if user.is_superuser:
            return SysLog.objects.all().filter()
        else:
            return []


def get_local_ip():
    """
    获取本机IP
    :return:
    """
    local_ip = ''
    if VUL_IP:
        return VUL_IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()
    return local_ip
