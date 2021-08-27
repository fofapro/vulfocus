#!/usr/bin/env python 
# -*- coding: UTF-8 -*- 
# @Time :2020/4/27 20:41 
# @Author :r4v3zn 
# @Site : 
# @File :tasks.py
from __future__ import absolute_import, unicode_literals
from celery import shared_task, chain
import uuid
import time
import socket
import docker
import traceback
import json
import django.utils.timezone as timezone
import random
from django.db.models import Q

from layout_image.bridge import get_project
from vulfocus.settings import client, api_docker_client, DOCKER_CONTAINER_TIME, VUL_IP, REDIS_POOL, DOCKER_COMPOSE
from dockerapi.common import DEFAULT_CONFIG
from dockerapi.models import ContainerVul, ImageInfo
from user.models import UserProfile
from docker.errors import NotFound, ImageNotFound, BuildError
from .models import TaskInfo
from dockerapi.common import R, HTTP_ERR
from dockerapi.models import SysLog
import datetime
from dockerapi.serializers import ImageInfoSerializer, ContainerVulSerializer
import redis
import requests
import os
import yaml
from layout_image.models import LayoutData, LayoutServiceContainer, LayoutService
from dockerapi.common import get_setting_config
r = redis.Redis(connection_pool=REDIS_POOL)
from django.db import transaction
import shutil
from ruamel.yaml import YAML


def create_image_task(image_info, user_info, request_ip, image_file=None):
    """
    创建镜像任务
    """
    user_id = user_info.id
    task_id = create_create_image_task(image_info=image_info, user_info=user_info)
    if user_info.is_superuser:
        image_name = image_info.image_name
        image_desc = image_info.image_desc
        image_vul_name = image_info.image_vul_name
        image_rank = image_info.rank
        task_info = TaskInfo.objects.filter(task_id=task_id).first()
        if image_file:
            task_msg = {}
            try:
                file_info = image_file.read()
                images = client.images.load(file_info)
                image = images[0]
                repo_tags = image.attrs["RepoTags"]
                if len(repo_tags) == 0:
                    # 移除本地镜像
                    try:
                        client.images.remove(image.id)
                    except Exception as e:
                        pass
                    task_msg = R.build(msg="文件镜像 Tag 不能为空")
                else:
                    config = image.attrs["ContainerConfig"]
                    port_list = []
                    if "ExposedPorts" in config:
                        port_list = config["ExposedPorts"]
                    else:
                        port_list = image.attrs['Config']['ExposedPorts']
                    ports = []
                    for port in port_list:
                        port = port.replace("/", "").replace("tcp", "").replace("udp", "")
                        ports.append(port)
                    image_name = repo_tags[0]
                    image_port = ",".join(ports)
                    image_info = ImageInfo.objects.filter(image_name=image_name).first()
                    if not image_info:
                        image_info = ImageInfo()
                    image_info.image_name = image_name
                    image_info.image_port = image_port
                    # image_vul_name
                    image_info.image_vul_name = image_name.replace("vulfocus/","") if not image_vul_name else image_vul_name
                    # image_desc
                    image_info.image_desc = image_name.replace("vulfocus/","") if not image_desc else image_desc
                    # rank
                    image_info.rank = 2.5 if image_rank > 5 or image_rank < 0.5 else image_rank
                    image_info.is_ok = True
                    image_info.save()
                    task_info.task_name = "拉取镜像："+image_name
                    task_info.task_status = 3
                    task_msg = R.ok(data="%s 添加成功" % (image_name, ))
            except Exception as e:
                traceback.print_exc()
                task_msg = R.err()
                try:
                    image_info.delete()
                except:
                    pass
                task_info.task_status = 4
            finally:
                task_info.task_msg = json.dumps(task_msg)
                task_info.update_date = timezone.now()
                task_info.save()
        elif image_name:
            # 创建任务
            # create_image(task_id=task_id)
            create_image.delay(task_id)
        else:
            R.build(msg="镜像文件或镜像名称不能为空")
        operation_args = ImageInfoSerializer(image_info).data
        sys_log = SysLog(user_id=user_id, operation_type="镜像", operation_name="创建", ip=request_ip,
                         operation_value=operation_args["image_vul_name"], operation_args=json.dumps(operation_args))
        sys_log.save()
    else:
        task_info = TaskInfo.objects.filter(task_id=task_id).first()
        task_info.task_msg = json.dumps(R.build(msg="权限不足"))
        task_info.task_status = 3
        task_info.update_date = timezone.now()
        task_info.save()
    return task_id


def create_compose_task(user_info, image_info, tag, request_ip):
    """
    创建docker-compose镜像任务
    """
    image_list = []
    local_images = [i.tags[0] for i in client.images.list() if i.tags]
    user_id = user_info.id
    task_id = create_create_image_task(image_info=image_info, user_info=user_info)
    task_infos = TaskInfo.objects.filter(task_id=task_id).first()
    if user_info.is_superuser:
        new_yaml = YAML(typ='safe')
        new_yaml.allow_duplicate_keys = True
        args_yaml = new_yaml.load(json.loads(image_info.original_yml))
        for services_name in args_yaml['services']:
            if "image" in args_yaml['services'][services_name]:
                image_name = args_yaml['services'][services_name]['image']
                if ':' not in image_name:
                    image_name = image_name + ":latest"
                all_arg = {"img_name": image_name, "images_name": image_info.image_name, 'args_yaml': json.dumps(args_yaml), 'tag':tag}
                if image_name:
                    task_info = TaskInfo(task_name="docker-compose相关镜像：" + image_name,
                                         user_id=user_id,
                                         task_status=1,
                                         task_msg=json.dumps({}),
                                         task_start_date=timezone.now(),
                                         operation_type=7,
                                         operation_args=json.dumps(all_arg),
                                         create_date=timezone.now(),
                                         update_date=timezone.now())
                    task_info.save()
                    task_id = task_info.task_id
                    image_list.append(image_name)
                    compose.delay(task_id)
    else:
        task_infos = TaskInfo.objects.filter(task_id=task_id).first()
        task_infos.task_msg = json.dumps(R.build(msg="权限不足"))
        task_infos.task_status = 4
        task_infos.update_date = timezone.now()
        task_infos.save()
    return image_list



def share_image_task(image_info, user_info, request_ip):
    """
    共享镜像
    :param image_info: 镜像信息
    :param user_info: 用户信息
    :param request_ip: 请求 IP
    :return:
    """
    task_id = create_share_image_task(image_info=image_info, user_info=user_info)
    operation_args = ImageInfoSerializer(image_info).data

    sys_log = SysLog(user_id=user_info.id, operation_type="镜像", operation_name="分享", ip=request_ip,
                     operation_value=operation_args["image_vul_name"], operation_args=json.dumps(operation_args))
    sys_log.save()
    share_image.delay(task_id)
    return task_id


def create_container_task(container_vul, user_info, request_ip):
    """
    创建漏洞容器
    :param container_vul: container vul
    :param user_info: user info
    :param request_ip: request ip
    :return:
    """
    image_info = container_vul.image_id
    user_id = user_info.id
    task_id = create_run_container_task(container_vul, user_info)
    if user_info.is_superuser or user_id == container_vul.user_id:
        operation_args = ImageInfoSerializer(image_info).data
        sys_log = SysLog(user_id=user_id, operation_type="容器", operation_name="启动", ip=request_ip,
                         operation_value=operation_args["image_vul_name"], operation_args=json.dumps(operation_args))
        sys_log.save()
        setting_config = get_setting_config()
        try:
            countdown = int(setting_config["time"])
        except:
            countdown = int(DEFAULT_CONFIG["time"])
        if countdown == 0:
            run_container.delay(container_vul.container_id, user_id, task_id, countdown)
        elif countdown != 0 and countdown > 60:
            # run_container(container_vul.container_id, user_id, task_id, countdown)
            setting_config = get_setting_config()
            if 'del_container' in setting_config:
                del_container = setting_config['del_container']
                if not del_container or del_container == 0 or del_container == '0':
                    add_chain_sig = chain(run_container.s(container_vul.container_id, user_id, task_id, countdown) |
                                          stop_container.s().set(countdown=countdown))
                else:
                    add_chain_sig = chain(run_container.s(container_vul.container_id, user_id, task_id, countdown) |
                                          delete_container.s().set(countdown=countdown))
                add_chain_sig.apply_async()
        else:
            task_info = TaskInfo.objects.filter(task_id=task_id).first()
            task_info.task_msg = json.dumps(R.build(msg="停止时间最小为 1 分钟"))
            task_info.task_status = 4
            task_info.update_date = timezone.now()
            task_info.save()
    else:
        task_info = TaskInfo.objects.filter(task_id=task_id).first()
        task_info.task_msg = json.dumps(R.build(msg="权限不足"))
        task_info.task_status = 3
        task_info.update_date = timezone.now()
        task_info.save()
    return task_id


def start_docker_compose(request, image_id, container_vul, user_info, request_ip, time_model_id):
    image_info = container_vul.image_id
    user_id = user_info.id
    task_id = create_run_container_task(container_vul, user_info)
    if user_info.is_superuser or user_id == container_vul.user_id:
        operation_args = ImageInfoSerializer(image_info).data

        sys_log = SysLog(user_id=user_id, operation_type="容器", operation_name="启动", ip=request_ip,
                         operation_value=operation_args["image_vul_name"], operation_args=json.dumps(operation_args))
        sys_log.save()
        setting_config = get_setting_config()
        try:
            countdown = int(setting_config["time"])
        except:
            countdown = int(DEFAULT_CONFIG["time"])
        if countdown == 0:
            run_docker_compose(container_vul.container_id, user_id, time_model_id, task_id, countdown)
        elif countdown != 0 and countdown > 60:
            setting_config = get_setting_config()
            if 'del_container' in setting_config:
                del_container = setting_config['del_container']
                if not del_container or del_container == 0 or del_container == '0':
                    add_chain_sig = chain(run_docker_compose.s(image_id, container_vul.container_id, user_id, time_model_id, task_id, countdown, ) |
                                          stop_docker_compose.s().set(countdown=countdown))
                else:
                    add_chain_sig = chain(run_docker_compose.s(image_id, container_vul.container_id, user_id, time_model_id, task_id, countdown, ) |
                                          stop_docker_compose.s().set(countdown=countdown))
                add_chain_sig.apply_async()
        else:
            task_info = TaskInfo.objects.filter(task_id=task_id).first()
            task_info.task_msg = json.dumps(R.build(msg="停止时间最小为 1 分钟"))
            task_info.task_status = 4
            task_info.update_date = timezone.now()
            task_info.save()
    else:
        task_info = TaskInfo.objects.filter(task_id=task_id).first()
        task_info.task_msg = json.dumps(R.build(msg="权限不足"))
        task_info.task_status = 3
        task_info.update_date = timezone.now()
        task_info.save()
    return task_id


def stop_container_task(container_vul, user_info, request_ip):
    """
    停止漏洞容器
    :param container_vul: container vul
    :param user_info: user info
    :param request_ip: request ip
    :return:
    """
    user_id = user_info.id
    task_id = create_stop_container_task(container_vul=container_vul, user_info=user_info)
    if user_info.is_superuser or user_id == container_vul.user_id:
        operation_args = ContainerVulSerializer(container_vul).data
        img_info = ImageInfo.objects.filter(image_id=operation_args['image_id']).first()
        sys_log = SysLog(user_id=user_id, operation_type="容器", operation_name="停止", ip=request_ip,
                         operation_value=operation_args["vul_name"], operation_args=json.dumps(operation_args))
        sys_log.save()
        # 下发停止容器任务
        if img_info.is_docker_compose == True:
            stop_docker_compose.delay(task_id)
        else:
            stop_container.delay(task_id)
    else:
        task_info = TaskInfo.objects.filter(task_id=task_id).first()
        task_info.task_msg = json.dumps(R.build(msg="权限不足"))
        task_info.task_status = 3
        task_info.update_date = timezone.now()
        task_info.save()
    return task_id


def delete_container_task(container_vul, user_info, request_ip):
    """
    删除漏洞容器
    :param container_vul: container vul
    :param user_info: user info
    :param request_ip: request ip
    :return:
    """
    user_id = user_info.id
    task_id = create_delete_container_task(container_vul=container_vul, user_info=user_info)
    if user_info.is_superuser or user_id == container_vul.user_id:
        operation_args = ContainerVulSerializer(container_vul).data
        img_info = ImageInfo.objects.filter(image_id=operation_args['image_id']).first()
        sys_log = SysLog(user_id=user_id, operation_type="容器", operation_name="删除", ip=request_ip,
                         operation_value=operation_args["vul_name"], operation_args=json.dumps(operation_args))
        sys_log.save()
        # 下发停止容器任务
        if img_info.is_docker_compose == True:
            delete_docker_compose.delay(task_id)
        else:
            delete_container.delay(task_id)
    else:
        task_info = TaskInfo.objects.filter(task_id=task_id).first()
        task_info.task_msg = json.dumps(R.build(msg="权限不足"))
        task_info.task_status = 3
        task_info.update_date = timezone.now()
        task_info.save()
    return task_id


@shared_task(name="tasks.run_docker_compose")
def run_docker_compose(image_id, container_id, user_id, time_model_id, task_id, countdown):
    img_info = ImageInfo.objects.filter(image_id=image_id).first()
    user_info = UserProfile.objects.filter(id=user_id).first()
    container_vul = ContainerVul.objects.filter(container_id=container_id).first()
    net_list = []
    net_name = 'docker-compose-dedicated'
    network_list = client.networks.list()
    for i in network_list:
        net_list.append(i.attrs['Name'])
    if net_name in net_list:
        pass
    else:
        ipam_pool = docker.types.IPAMPool(
            subnet='192.168.10.10/24',
            gateway='192.168.10.10'
        )
        ipam_config = docker.types.IPAMConfig(
            pool_configs=[ipam_pool]
        )
        net_work = client.networks.create(
            net_name,
            driver='bridge',
            ipam=ipam_config,
            scope='local',
        )
        net_work_client_id = str(net_work.id)
    if img_info.is_docker_compose == True:
        if container_vul.container_status == 'stop':
            container_vul.container_status = "running"
            task_info = TaskInfo.objects.filter(task_id=task_id).first()
            compose_path = os.path.join(DOCKER_COMPOSE, str(container_vul.container_id))
            container_list = get_project(compose_path).up()
            try:
                with transaction.atomic():
                    for container in container_list:
                        docker_container_id = container.id
                        docker_container = client.containers.get(container.id)
                        container_vul_img = ContainerVul.objects.filter(docker_container_id=docker_container_id).first()
                        container_vul_img.container_status = 'running'
                        container_vul_img.save()
                        args = {
                            "image_name": img_info.image_name,
                            "user_id": user_id,
                            "image_port": img_info.image_port
                        }
                        task_start_date = timezone.now()
                        if countdown != 0 and countdown >= 60:
                            task_end_date = task_start_date + datetime.timedelta(seconds=countdown)
                        elif countdown == 0:
                            task_end_date = None
                        else:
                            countdown = int(DEFAULT_CONFIG["time"])
                            task_end_date = task_start_date + datetime.timedelta(seconds=countdown)
                        if "running" == docker_container.status:
                            msg_data = R.ok(data={
                                "host": container_vul.vul_host,
                                "port": json.loads(container_vul.vul_port),
                                "id": str(container_vul.container_id),
                                "status": "running",
                                "start_date": int(task_start_date.timestamp()),
                                "end_date": 0 if not task_end_date else int(task_end_date.timestamp())
                            })
                            search_task = TaskInfo.objects.filter(user_id=user_id, task_msg=json.dumps(msg_data),
                                                                  operation_type=2,
                                                                  operation_args=json.dumps(args),
                                                                  task_end_date=task_end_date,
                                                                  task_name="运行容器：" + img_info.image_name).order_by(
                                "-create_date").first()
                            if not search_task:
                                task_info.task_status = 3
                                task_info.task_msg = json.dumps(msg_data)
                                task_info.update_date = timezone.now()
                                task_info.operation_args = json.dumps(args)
                                task_info.save()
                                task_id = str(task_info.task_id)
                            else:
                                task_info.delete()
                                search_task.task_id = task_id
                                search_task.task_status = 3
                                search_task.update_date = timezone.now()
                                search_task.save()
                                task_id = str(search_task.task_id)
                container_vul.save()
            except Exception as e:
                traceback.print_exc()
        else:
            vulport = {}
            yml_c = json.loads(img_info.docker_compose_yml)
            yml_c['networks'] = {"default": {"external": {"name": "docker-compose-dedicated"}}}
            yml_content = yaml.dump(yml_c)
            env_content = json.loads(img_info.docker_compose_env)
            random_list = []
            result_port_list = []
            container_flag = "flag-{bmh%s}" % (uuid.uuid4(),)
            for _port in env_content:
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
                for one_port in json.loads(img_info.compose_env_port):
                    split_port = one_port.split(':')
                    if _port in split_port[0]:
                        vulport[random_port] = split_port[1]
            vulport = json.dumps(vulport)
            original_port = ""
            for port_str in random_list:
                if random_list[-1] == port_str:
                    original_port = original_port + port_str
                else:
                    original_port = original_port + port_str + ","
            compose_path = os.path.join(DOCKER_COMPOSE, str(container_vul.container_id))
            original_ip = get_local_ip()
            original_container_vul = container_vul
            original_container_vul.docker_compose_path = compose_path
            original_container_vul.container_status = "running"
            original_container_vul.container_port = original_port
            original_container_vul.container_flag = container_flag
            original_container_vul.vul_port = vulport
            original_container_vul.vul_host = original_ip + ":" + original_port
            original_container_vul.is_docker_compose_correlation = False
            original_container_vul.save()
            if not os.path.exists(compose_path):
                os.makedirs(compose_path)
            docker_compose_file = os.path.join(compose_path, "docker-compose.yml")
            with open(docker_compose_file, "w", encoding="utf-8") as f:
                f.write(yml_content)
            env_file = os.path.join(compose_path, ".env")
            with open(env_file, "w", encoding="utf-8") as f:
                f.write("\n".join(result_port_list))
            try:
                task_info = TaskInfo.objects.filter(task_id=task_id).first()
                container_list = get_project(compose_path).up()
                with transaction.atomic():
                    for container in container_list:
                        docker_container_id = container.id
                        # service_id = container.service
                        container_host = ""
                        container_port = ""
                        docker_container = client.containers.get(container.id)
                        command = 'touch /tmp/%s' % (container_flag,)
                        execute_result = docker_container_run(docker_container, command)
                        if execute_result["status"] == 500:
                            raise Exception(execute_result["msg"])
                        container_ports = container.ports
                        if len(container_ports) == 0:
                            try:
                                container_ports = docker_container.attrs["NetworkSettings"]["Ports"]
                            except Exception as e:
                                pass
                        vul_host_list = []
                        vul_ip = get_local_ip()
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
                        if len(port_dict) > 0:
                            container_port = json.dumps(port_dict, ensure_ascii=False)
                        container_status = execute_result["data"]["status"]
                        if len(vul_host_list) > 0:
                            container_host = ",".join(vul_host_list)
                        container_vul_img = ContainerVul(image_id=img_info, user_id=user_info.id, vul_host=container_host,
                                                         container_status=container_status,
                                                         docker_container_id=docker_container_id,
                                                         vul_port=container_port,
                                                         container_port=container_port,
                                                         time_model_id=time_model_id,
                                                         create_date=timezone.now(),
                                                         container_flag=container_flag,
                                                         is_docker_compose_correlation=True)
                        container_vul_img.save()
                args = {
                    "image_name": img_info.image_name,
                    "user_id": user_id,
                    "image_port": img_info.image_port
                }
                task_start_date = timezone.now()
                if countdown != 0 and countdown >= 60:
                    task_end_date = task_start_date + datetime.timedelta(seconds=countdown)
                elif countdown == 0:
                    task_end_date = None
                else:
                    countdown = int(DEFAULT_CONFIG["time"])
                    task_end_date = task_start_date + datetime.timedelta(seconds=countdown)
                if "running" == docker_container.status:
                    msg_data = R.ok(data={
                        "host": original_container_vul.vul_host,
                        "port": json.loads(original_container_vul.vul_port),
                        "id": str(original_container_vul.container_id),
                        "status": "running",
                        "start_date": int(task_start_date.timestamp()),
                        "end_date": 0 if not task_end_date else int(task_end_date.timestamp())
                    })
                    search_task = TaskInfo.objects.filter(user_id=user_id, task_msg=json.dumps(msg_data), operation_type=2,
                                                          operation_args=json.dumps(args), task_end_date=task_end_date,
                                                          task_name="运行容器：" + img_info.image_name).order_by("-create_date").first()
                    if not search_task:
                        task_info.task_status = 3
                        task_info.task_msg = json.dumps(msg_data)
                        task_info.update_date = timezone.now()
                        task_info.operation_args = json.dumps(args)
                        task_info.save()
                        task_id = str(task_info.task_id)
                    else:
                        task_info.delete()
                        search_task.task_id = task_id
                        search_task.task_status = 3
                        search_task.update_date = timezone.now()
                        search_task.save()
                        task_id = str(search_task.task_id)
            except Exception as e:
                traceback.print_exc()
        return create_stop_container_task(container_vul,user_info)


@shared_task(name="tasks.stop_docker_compose")
def stop_docker_compose(task_id):
    task_info = TaskInfo.objects.filter(task_id=task_id, task_status=1).first()
    if not task_info:
        return
    operation_args = task_info.operation_args
    args = json.loads(operation_args)
    container_id = args["container_id"]
    user_id = args["user_id"]
    image_name = args["image_name"]
    image_info = ImageInfo.objects.filter(image_name=image_name).first()
    container_vul = ContainerVul.objects.filter(container_id=container_id).first()
    compose_path = container_vul.docker_compose_path
    try:
        with transaction.atomic():
            container_list = get_project(compose_path).stop()
            if container_list:
                for container in container_list:
                    container_id = container.id
                    container = ContainerVul.objects.filter(docker_container_id=container_id).update(
                        container_status="stop")
                    container.save()
            all_container = ContainerVul.objects.filter(
                Q(user_id=user_id) & Q(image_id=image_info.image_id) &
                Q(container_status="running")).all()
            if all_container:
                for corrtlation_container in all_container:
                    corrtlation_container.container_status = 'stop'
                    corrtlation_container.save()
            container_vul.container_status = 'stop'
            container_vul.save()
            msg = R.ok(msg="停止成功")
    except Exception:
        msg = R.err(msg="停止失败，服务器内部错误")
    task_info.task_status = 3
    task_info.task_msg = json.dumps(msg)
    task_info.update_date = timezone.now()
    task_info.save()
    print("停止漏洞容器成功，任务ID：%s" % (task_id,))


@shared_task(name="tasks.delete_docker_compose")
def delete_docker_compose(task_id):
    task_info = TaskInfo.objects.filter(task_id=task_id, task_status=1).first()
    if not task_info:
        return
    operation_args = task_info.operation_args
    args = json.loads(operation_args)
    user_id = args["user_id"]
    container_id = args["container_id"]
    image_name = args["image_name"]
    user_info = UserProfile.objects.filter(id=user_id).first()
    image_info = ImageInfo.objects.filter(image_name=image_name).first()
    # 删除容器
    container_vul = ContainerVul.objects.filter(Q(container_id=container_id)
                                                     & ~Q(docker_compose_path="") & ~Q(container_status='delete')).first()
    con_user_id = container_vul.user_id
    if container_vul.container_status == 'running':
        compose_path = container_vul.docker_compose_path
        try:
            with transaction.atomic():
                container_list = get_project(compose_path).stop()
                if container_list:
                    for container in container_list:
                        container_id = container.id
                        container = ContainerVul.objects.filter(docker_container_id=container_id).update(
                            container_status="stop")
                        container.save()
                all_container = ContainerVul.objects.filter(
                    Q(user_id=user_id) & Q(image_id=image_info.image_id) &
                    Q(container_status="running")).all()
                if all_container:
                    for corrtlation_container in all_container:
                        corrtlation_container.container_status = 'stop'
                        corrtlation_container.save()
                container_vul.container_status = 'stop'
                container_vul.save()
        except Exception:
            msg = R.err(msg="删除失败，服务器内部错误")
    all_stop_container = ContainerVul.objects.filter(Q(user_id=con_user_id) & Q(image_id=image_info.image_id) &
                    Q(container_status="stop") & Q(docker_compose_path="")).all()
    if all_stop_container:
        compose_path = container_vul.docker_compose_path
        for corrtlation_container in all_stop_container:
            docker_container_id = corrtlation_container.docker_container_id
            try:
                # 连接Docker容器
                docker_container = client.containers.get(docker_container_id)
                # 删除容器
                docker_container.remove(force=True)
            except Exception:
                pass
            finally:
                corrtlation_container.container_status = "delete"
                corrtlation_container.docker_container_id = ""
                # 保存成功
                corrtlation_container.save()
        if os.path.exists(compose_path) == True:
            shutil.rmtree(compose_path)
    container_vul.docker_compose_path = ""
    container_vul.container_status = "delete"
    container_vul.save()
    msg = R.ok(msg="删除成功")
    task_info.task_status = 3
    task_info.task_msg = json.dumps(msg)
    task_info.update_date = timezone.now()
    task_info.save()
    print("删除漏洞容器成功，任务ID：%s" % (task_id,))



@shared_task(name="tasks.run_container")
def run_container(container_id, user_id, tmp_task_id, countdown):
    """
    运行 docker 容器
    :param container_id: 漏洞容器数据库 id
    :param user_id: 用户ID
    :param tmp_task_id: 任务ID
    :param countdown 定时
    """
    container_vul = ContainerVul.objects.filter(container_id=container_id).first()
    user_info = UserProfile.objects.filter(id=user_id).first()
    container_id = container_vul.docker_container_id
    image_info = container_vul.image_id
    image_name = image_info.image_name
    image_port = image_info.image_port
    user_id = user_info.id
    docker_container = None
    msg = {}
    """
    创建启动任务
    """
    args = {
        "image_name": image_name,
        "user_id": user_id,
        "image_port": image_port
    }
    task_id = ""
    task_info = TaskInfo.objects.filter(task_id=tmp_task_id).first()
    # run container execute command
    command = ""
    vul_flag = container_vul.container_flag
    container_port = container_vul.container_port
    vul_port = {}
    if container_vul.vul_port:
        vul_port = json.loads(container_vul.vul_port)
    vul_host = container_vul.vul_host
    if container_id:
        # check container
        check_rsp = check_container(container_id)
        if check_rsp["flag"]:
            docker_container = check_rsp["container"]
            # set container_flag
            vul_flag = container_vul.container_flag
    # if container by delete , create a container
    if not docker_container:
        port_list = image_port.split(",")
        port_dict = {}
        random_list = []
        for port in port_list:
            random_port = ''
            for i in range(20):
                # random port
                random_port = str(random.randint(8000, 65536))
                if random_port in random_list or ContainerVul.objects.filter(container_port=random_port).first():
                    continue
                break
            if not random_port:
                msg = R.err(msg="端口无效")
                break
            random_list.append(random_port)
            port_dict['%s/tcp' % (port,)] = int(random_port)
        # 端口重复，无法进行创建
        if len(msg) > 0 or msg:
            task_info.task_msg = json.dumps(msg)
            task_info.update_date = timezone.now()
            # except
            task_info.task_status = 4
            task_info.save()
            return str(task_info.task_id)
        container_port = ",".join(random_list)
        """
        random port
        """
        for tmp_port in port_dict:
            tmp_random_port = port_dict[tmp_port]
            tmp_port = tmp_port.replace("/tcp", "")
            vul_port[tmp_port] = str(tmp_random_port)
        try:
            client.images.get(image_name)
        except Exception as e:
            msg = R.build(msg="镜像不存在")
            task_info.task_msg = json.dumps(msg)
            task_info.update_date = timezone.now()
            # except
            task_info.task_status = 4
            task_info.save()
            image_info.is_ok = False
            image_info.save()
            return str(task_info.task_id)
        vul_flag = "flag-{bmh%s}" % (uuid.uuid4(),)
        if container_vul.container_flag:
            vul_flag = container_vul.container_flag
        try:
            docker_container = client.containers.run(image_name, ports=port_dict, detach=True, environment={"vul_flag": vul_flag})
        except ImageNotFound:
            msg = R.build(msg="镜像不存在")
            task_info.task_msg = json.dumps(msg)
            task_info.update_date = timezone.now()
            # except
            task_info.task_status = 4
            task_info.save()
            image_info.is_ok = False
            image_info.save()
            return str(task_info.task_id)

        command = 'touch /tmp/%s' % (vul_flag,)
        vul_host = get_local_ip() + ":" + container_port
    task_start_date = timezone.now()
    if countdown != 0 and countdown >= 60:
        task_end_date = task_start_date + datetime.timedelta(seconds=countdown)
    elif countdown == 0:
        task_end_date = None
    else:
        countdown = int(DEFAULT_CONFIG["time"])
        task_end_date = task_start_date + datetime.timedelta(seconds=countdown)
    if "running" == docker_container.status:
        msg_data = R.ok(data={
            "host": container_vul.vul_host,
            "port": container_vul.vul_port,
            "id": str(container_vul.container_id),
            "status": "running",
            "start_date": int(task_start_date.timestamp()),
            "end_date": 0 if not task_end_date else int(task_end_date.timestamp())
        })
        search_task = TaskInfo.objects.filter(user_id=user_id, task_msg=json.dumps(msg_data), operation_type=2,
                                              operation_args=json.dumps(args), task_end_date=task_end_date,
                                              task_name="运行容器：" + image_name).order_by("-create_date").first()
        if not search_task:
            task_info.task_status = 3
            task_info.task_msg = json.dumps(msg_data)
            task_info.update_date = timezone.now()
            task_info.operation_args = json.dumps(args)
            task_info.save()
            task_id = str(task_info.task_id)
        else:
            task_info.delete()
            search_task.task_id = tmp_task_id
            search_task.task_status = 3
            search_task.update_date = timezone.now()
            search_task.save()
            task_id = str(search_task.task_id)
    else:
        task_info.save()
        docker_container.start()
        msg = docker_container_run(docker_container, command=command)
        if msg["status"] == HTTP_ERR:
            try:
                container_vul.delete()
            except Exception:
                pass
            # except
            task_info.task_status = 4
        else:
            container_status = msg["data"]["status"]
            msg["data"]["host"] = vul_host
            msg["data"]["port"] = vul_port
            msg["data"]["id"] = str(container_vul.container_id)
            msg["data"]["status"] = container_status
            msg["data"]["start_date"] = int(task_start_date.timestamp())
            msg["data"]["end_date"] = 0 if not task_end_date else int(task_end_date.timestamp())
            # 容器状态
            container_vul.container_status = container_status
            # 容器 id
            container_vul.docker_container_id = str(docker_container.id)
            # 漏洞 HOST
            container_vul.vul_host = vul_host
            # 漏洞端口
            container_vul.vul_port = json.dumps(vul_port)
            # 容器端口映射关系
            container_vul.container_port = container_port
            # 验证 flag
            container_vul.container_flag = vul_flag
            container_vul.save()
            task_start_date = timezone.now()
            # start 时间
            task_info.task_start_date = task_start_date
            task_info.task_end_date = task_end_date
            task_info.task_status = 3
        task_info.task_msg = json.dumps(msg)
        task_info.update_date = timezone.now()
        task_info.save()
        task_id = str(task_info.task_id)
    print("启动漏洞容器成功，任务ID：%s" % (task_id, ))
    return create_stop_container_task(container_vul,user_info)


@shared_task(name="tasks.stop_container")
def stop_container(task_id):
    """
    停止 docker 容器
    :param task_id: task id
    """
    task_info = TaskInfo.objects.filter(task_id=task_id, task_status=1).first()
    if not task_info:
        return
    operation_args = task_info.operation_args
    args = json.loads(operation_args)
    container_id = args["container_id"]
    container_vul = ContainerVul.objects.filter(container_id=container_id).first()
    msg = R.ok(msg="停止成功")
    if container_vul:
        docker_container_id = container_vul.docker_container_id
        try:
            # 连接 Docker 容器
            docker_container = client.containers.get(docker_container_id)
            docker_container.stop()
            container_vul.container_status = 'stop'
            container_vul.save()
            msg = R.ok(msg="停止成功")
        except NotFound:
            container_vul.delete()
            msg = R.ok(msg="停止成功")
        except Exception:
            msg = R.err(msg="停止失败，服务器内部错误")
    # execute finish
    task_info.task_status = 3
    task_info.task_msg = json.dumps(msg)
    task_info.update_date = timezone.now()
    task_info.save()
    print("停止漏洞容器成功，任务ID：%s" % (task_id, ))


@shared_task(name="tasks.delete_container")
def delete_container(task_id):
    """
    删除容器任务
    :param task_id: 任务id
    """
    task_info = TaskInfo.objects.filter(task_id=task_id, task_status=1).first()
    if not task_info:
        return
    operation_args = task_info.operation_args
    args = json.loads(operation_args)
    container_id = args["container_id"]
    # 删除容器
    container_vul = ContainerVul.objects.filter(Q(docker_container_id__isnull=False), ~Q(docker_container_id=''),
                                                container_id=container_id).first()
    msg = R.ok(msg="删除成功")
    if container_vul:
        # docker 连接容器ID
        docker_container_id = container_vul.docker_container_id
        try:
            # 连接Docker容器
            docker_container = client.containers.get(docker_container_id)
            # 停止容器运行
            docker_container.stop()
            # 删除容器
            docker_container.remove(force=True)
        except Exception:
            pass
        finally:
            container_vul.container_status = "delete"
            container_vul.docker_container_id = ""
            # 保存成功
            container_vul.save()
            # container_vul.delete()
            msg = R.ok(msg="删除成功")
    task_info.task_status = 3
    task_info.task_msg = json.dumps(msg)
    task_info.update_date = timezone.now()
    task_info.save()
    print("删除漏洞容器成功，任务ID：%s" % (task_id, ))


@shared_task(name="tasks.create_image")
def create_image(task_id):
    """
    创建镜像名称
    """
    task_info = TaskInfo.objects.filter(task_id=task_id, task_status=1).first()
    if not task_info:
        return
    operation_args = task_info.operation_args
    args = json.loads(operation_args)
    image_name = args["image_name"].strip()
    image_info = ImageInfo.objects.filter(image_name=image_name).first()
    if not image_info:
        image_desc = image_name
        image_rank = 2.5
        image_vul_name = image_desc
        image_info = ImageInfo(image_name=image_name, image_desc=image_desc, rank=image_rank, image_vul_name=image_vul_name)
    image = None
    msg = {}
    try:
        image = client.images.get(image_name)
    except Exception as e:
        image_info.is_ok = False
        image_info.save()
        try:
            last_info = {}
            progress_info = {
                "total": 0,
                "progress_count": 0,
                "progress": round(0.0, 2),
            }
            black_list = ["total", "progress_count", "progress"]
            for line in api_docker_client.pull(image_name, stream=True, decode=True):
                if "status" in line and "progressDetail" in line and "id" in line:
                    id = line["id"]
                    status = line["status"]
                    if len(line["progressDetail"]) > 0:
                        try:
                            current = line["progressDetail"]["current"]
                            total = line["progressDetail"]["total"]
                            line["progress"] = round((current / total) * 100, 2)
                            if (current / total) > 1:
                                line["progress"] = round(0.99 * 100, 2)
                        except:
                            line["progress"] = round(1 * 100, 2)
                    else:
                        if (("Download" in status or "Pull" in status) and ("complete" in status)) or ("Verifying" in status) or \
                                ("Layer" in status and "already" in status and "exists" in status):
                            line["progress"] = round(100.00, 2)
                        else:
                            line["progress"] = round(0.00, 2)
                    progress_info[id] = line
                    progress_info["total"] = len(progress_info) - len(black_list)
                    progress_count = 0
                    for key in progress_info:
                        if key in black_list:
                            continue
                        if 100.00 != progress_info[key]["progress"]:
                            continue
                        progress_count += 1
                    progress_info["progress_count"] = progress_count
                    progress_info["progress"] = round((progress_count/progress_info["total"])*100, 2)
                    r.set(str(task_id), json.dumps(progress_info,ensure_ascii=False))
                    print(json.dumps(progress_info, ensure_ascii=False))
                last_info = line
            if "status" in last_info and ("Downloaded newer image for" in last_info["status"] or "Image is up to date for" in last_info["status"]):
                image = client.images.get(image_name)
            else:
                raise Exception
        except ImageNotFound:
            msg = R.build(msg="%s 不存在" % (image_name,))
        except Exception:
            traceback.print_exc()
            msg = R.err(msg="%s 添加失败" % (image_name,))
    if image:
        config = image.attrs["ContainerConfig"]
        port_list = []
        if "ExposedPorts" in config:
            port_list = config["ExposedPorts"]
        else:
            port_list = image.attrs['Config']['ExposedPorts']
        ports = []
        for port in port_list:
            port = port.replace("/", "").replace("tcp", "").replace("udp", "")
            ports.append(port)
        image_port = ",".join(ports)
        image_info.image_port = image_port
        image_info.is_ok = True
        image_info.save()
        msg = R.ok(msg="%s 添加成功" % (image_name,), data=json.dumps({"image_port": image_port}))
        task_info.task_status = 3
    else:
        task_info.task_status = 4
    task_info.task_msg = json.dumps(msg)
    task_info.save()


@shared_task(name="tasks.compose")
def compose(task_id):
    '''
    compose 相关镜像下载
    image_info docker-compose 镜像 非相关镜像
    '''

    task_info = TaskInfo.objects.filter(task_id=task_id, task_status=1).first()
    operation_args = task_info.operation_args
    args = json.loads(operation_args)
    images_name = args['images_name']
    yaml_args = json.loads(args['args_yaml'])
    image_name = args['img_name']
    img_list = []
    image_info = ImageInfo.objects.filter(image_name=images_name).first()
    img_name = image_info.image_name
    for services_name in yaml_args['services']:
        if "image" in yaml_args['services'][services_name]:
            name = yaml_args['services'][services_name]['image']
            img_list.append(name)
    if not task_info:
        return
    task_info.task_msg = json.dumps(img_name)
    task_info.task_status = 2
    task_info.save()
    image = None
    msg = {}
    try:
        image = client.images.get(image_name)
    except Exception as e:
        try:
            last_info = {}
            progress_info = {
                "total": 0,
                "progress_count": 0,
                "progress": round(0.0, 2),
            }
            black_list = ["total", "progress_count", "progress"]
            for line in api_docker_client.pull(image_name, stream=True, decode=True):
                print(line)
                if "status" in line and "progressDetail" in line and "id" in line:
                    id = line["id"]
                    status = line["status"]
                    if len(line["progressDetail"]) > 0:
                        try:
                            current = line["progressDetail"]["current"]
                            total = line["progressDetail"]["total"]
                            line["progress"] = round((current / total) * 100, 2)
                            if (current / total) > 1:
                                line["progress"] = round(0.99 * 100, 2)
                        except:
                            line["progress"] = round(1 * 100, 2)
                    else:
                        if (("Download" in status or "Pull" in status) and ("complete" in status)) or ("Verifying" in status) or \
                                ("Layer" in status and "already" in status and "exists" in status):
                            line["progress"] = round(100.00, 2)
                        else:
                            line["progress"] = round(0.00, 2)
                    progress_info[id] = line
                    progress_info["total"] = len(progress_info) - len(black_list)
                    progress_count = 0
                    for key in progress_info:
                        if key in black_list:
                            continue
                        if 100.00 != progress_info[key]["progress"]:
                            continue
                        progress_count += 1
                    progress_info["progress_count"] = progress_count
                    progress_info["progress"] = round((progress_count/progress_info["total"])*100, 2)
                    r.set(str(task_id), json.dumps(progress_info,ensure_ascii=False))
                    print(json.dumps(progress_info, ensure_ascii=False))
                last_info = line
            if "status" in last_info and ("Downloaded newer image for" in last_info["status"] or "Image is up to date for" in last_info["status"]):
                image = client.images.get(image_name)
            else:
                raise Exception
        except ImageNotFound:
            task_info.task_status = 4
            traceback.print_exc()
            msg = R.build(msg="%s 不存在" % (image_name,))
        except Exception:
            task_info.task_status = 4
            traceback.print_exc()
            msg = R.err(msg="%s 下载失败" % (image_name,))
    if image:
        try:
            task_info.task_status = 3
            task_info.save()
        except Exception:
            task_info.task_status = 4
            task_info.save()
            msg = R.err(msg="%s 下载失败" % (image_name,))
    try:
        for img in img_list:
            image = client.images.get(img)
        image_info.is_ok = True
        image_info.save()
    except Exception:
        msg = R.err(msg="下载未完成" )
    task_info.task_msg = json.dumps(msg)
    task_info.save()



@shared_task(name="tasks.share_image")
def share_image(task_id):
    """
    贡献镜像
    :param task_id: 任务 id
    :return:
    """
    task_info = TaskInfo.objects.filter(task_id=task_id, task_status=1).first()
    operation_args = task_info.operation_args
    args = json.loads(operation_args)
    share_username = args["share_username"].strip()
    image_name = args["image_name"].strip()
    username = args["username"].strip()
    password = args["pwd"].strip()
    msg = R.ok(msg="分享成功")
    try:
        client.login(username, password)
        new_image_name = image_name.split(":")[0]+":"+share_username
        if new_image_name.rfind("/") > -1:
            r_image_info = new_image_name[:new_image_name.rfind("/")]
            if r_image_info.rfind("/") > -1:
                repo_tmp = r_image_info[:r_image_info.rfind("/")]
                repo_name = "/".join([repo_tmp, username, new_image_name[new_image_name.rfind("/")+1:]])
            else:
                repo_name = "/".join([username, new_image_name[new_image_name.rfind("/")+1:]])
        else:
            repo_name = "/".join([username, new_image_name])
        new_image_name = repo_name
        tag_flag = api_docker_client.tag(image_name, new_image_name)
        if tag_flag:
            last_info = {}
            progress_info = {
                "total": 0,
                "progress_count": 0,
                "progress": round(0.0, 2),
            }
            black_list = ["total", "progress_count", "progress"]
            for line in api_docker_client.push(new_image_name, stream=True, decode=True, auth_config={"username": username, "password": password}):
                if "status" in line and "progressDetail" in line and "id" in line:
                    id = line["id"]
                    status = line["status"]
                    if len(line["progressDetail"]) > 0:
                        try:
                            current = line["progressDetail"]["current"]
                            total = line["progressDetail"]["total"]
                            line["progress"] = round((current / total) * 100, 2)
                            if (current / total) > 1:
                                line["progress"] = round(0.99 * 100, 2)
                        except:
                            line["progress"] = round(1 * 100, 2)
                    else:
                        if ("Pushed" in status) or ("Verifying" in status) or \
                                ("Layer" in status and "already" in status and "exists" in status) or ("Mounted" in status and "from" in status):
                            line["progress"] = round(100.00, 2)
                        else:
                            line["progress"] = round(0.00, 2)
                    progress_info[id] = line
                    progress_info["total"] = len(progress_info) - len(black_list)
                    progress_count = 0
                    for key in progress_info:
                        if key in black_list:
                            continue
                        if 100.00 != progress_info[key]["progress"]:
                            continue
                        progress_count += 1
                    progress_info["progress_count"] = progress_count
                    progress_info["progress"] = round((progress_count/progress_info["total"])*100, 2)
                    r.set(str(task_id), json.dumps(progress_info,ensure_ascii=False))
                    print(json.dumps(progress_info, ensure_ascii=False))
                last_info = line
            if "error" in last_info and last_info["error"]:
                task_info.task_msg = R.build(msg="原%s构建新镜像%s失败，错误信息：%s" % (image_name, new_image_name, str(last_info["error"]),))
                task_info.task_status = 4
            elif "progressDetail" in last_info and "aux" in last_info and share_username in last_info["aux"]["Tag"]:
                image_info = ImageInfo.objects.filter(image_name=image_name).first()
                if image_info:
                    image_info.is_share = True
                    image_info.save()
                msg = R.ok(msg="%s 分享成功" % (image_name,))
            else:
                msg = R.build(msg="%s 分享失败" % (image_name,))
        else:
            task_info.task_msg = R.build(msg="原%s构建新镜像%s失败" % (image_name, new_image_name,))
            task_info.task_status = 4
    except docker.errors.APIError as api_error:
        msg = R.build(msg="Dockerhub 用户名或 Dockerhub Token 错误")
        task_info.task_status = 4
    except Exception as e:
        msg = R.build(msg="%s 分享失败，错误信息：%s" % (image_name, str(e),))
        task_info.task_status = 4
    task_info.task_status = 3
    task_info.task_msg = json.dumps(msg)
    task_info.save()


@shared_task(name="tasks.update_images")
def update_images():
    """
    定时获取dockerhub上的镜像信息
    """
    url = "https://hub.docker.com/v2/repositories/vulfocus/?ordering=last_updated&page=1&page_size=1"
    res = requests.get(url).content
    req = json.loads(res)
    count = req['count']
    num = count/100
    for item_num in range(int(num)+1):
        new_url = "https://hub.docker.com/v2/repositories/vulfocus/?ordering=last_updated&page={}&page_size=100".format(item_num+1)
        new_res = requests.get(new_url).content
        new_req = json.loads(new_res)
        if "results" not in new_req:
            break
        result = new_req['results']
        image_names = list(ImageInfo.objects.all().values_list('image_name', flat=True))
        try:
            for docker_image_info in result:
                image_name ="vulfocus/%s" % (docker_image_info['name'],) + ':latest'
                if image_name in image_names:
                    continue
                if image_name == "vulfocus/vulfocus:latest":
                    continue
                image_vul_name = image_name[:image_name.rfind(":")]
                # 替换 CVE CNVD CNNVD _
                if "cve" in image_vul_name:
                    image_vul_name =image_vul_name.replace("cve", "CVE")
                if "cnvd" in image_vul_name:
                    image_vul_name = image_vul_name.replace("cnvd", "CNVD")
                if "cnnvd" in image_vul_name:
                    image_vul_name = image_vul_name.replace("cnnvd", "CNNVD")
                if "_" in image_vul_name:
                    image_vul_name = image_vul_name.replace("_", "-")
                image_info = ImageInfo(image_name=image_name, image_vul_name=image_vul_name, image_desc="", rank=2.5,
                                       is_ok=False, create_date=timezone.now(), update_date=timezone.now())
                image_info.save()
        except Exception as e:
            pass


@shared_task(name="tasks.download_images")
def download_images():
    """
    同步漏洞镜像信息
    """
    setting_config = get_setting_config()
    is_synchronization = setting_config['is_synchronization']
    if not is_synchronization or is_synchronization == 0 or is_synchronization == '0':
        return
    image_info_list = ImageInfo.objects.all()
    user = UserProfile.objects.filter(is_superuser=True).order_by('date_joined').first()
    for image_info in image_info_list:
        create_image_task(image_info, user, '127.0.0.1')


@shared_task(name="tasks.check_images")
def check_images():
    """
    定期检测镜像状态
    """
    image_info_list = ImageInfo.objects.all()
    local_images = [i.tags[0] for i in client.images.list() if i.tags]
    for image_info in image_info_list:
        image_name = image_info.image_name
        if image_info.is_docker_compose == True:
            compose_yml = json.loads(image_info.docker_compose_yml)
            flag = True
            for services_name in compose_yml['services']:
                if "image" in compose_yml['services'][services_name]:
                    image_name = compose_yml['services'][services_name]['image']
                    image_name_tag = image_name
                    if ':' not in image_name_tag:
                        image_name_tag = image_name_tag + ":latest"
                    if image_name in local_images or image_name_tag in local_images:
                        continue
                    else:
                        flag = False
                if flag == False:
                    image_info.is_ok = False
                    image_info.save()
                    print("【检测镜像】%s 不存在" % image_name, )
                    break
            if flag == True:
                image_info.is_ok = True
                image_info.save()
                print("【检测镜像】%s 存在" % image_name, )
        else:
            try:
                client.images.get(image_name)
                image_info.is_ok = True
                image_info.save()
                print("【检测镜像】%s 存在" % image_name, )
            except Exception as e:
                image_info.is_ok = False
                image_info.save()
                print("【检测镜像】%s 不存在" % image_name, )


# @shared_task(name="tasks.check_layouts")
# def check_layouts():
#     """
#     定期检测编排环境状态
#     """
#     layout_data_list = LayoutData.objects.filter().all()
#     for layout_data in layout_data_list:
#         layout_path = layout_data.layout_path
#         if not os.path.exists(layout_path):
#             layout_data.status = 'stop'
#             LayoutServiceContainer.objects.filter(layout_user_id=layout_data).update(container_status="stop")
#             layout_data.save()
#         else:
#             container_list = get_project(layout_path).containers(stopped=True)
#             for container in container_list:
#                 service_info = LayoutService.objects.filter(service_name=container.service, layout_id=layout_data.layout_id).first()
#                 image_info = service_info.image_id
#                 container
#                 service_container = LayoutServiceContainer.objects.filter(service_id=service_info, layout_user_id=layout_data,image_id=image_info).first()
#                 service_container.container_status = ''


# @shared_task(name="tasks.timing_imgs")
# def timing_imgs():
#     """
#     定时获取官网镜像信息
#     """
#     try:
#         url = "http://vulfocus.fofa.so:8000/imgs/info"
#         res = requests.get(url, verify=False).content
#         req = json.loads(res)
#         image_names = list(ImageInfo.objects.all().values_list('image_name', flat=True))
#         for item in req:
#             if item['image_name'] in image_names:
#                 if item['image_name'] == "vulfocus/vulfocus:latest":
#                     continue
#                 single_img = ImageInfo.objects.filter(image_name__contains=item['image_name']).first()
#                 if single_img.image_vul_name != item['image_vul_name'] or single_img.image_vul_name == "":
#                     single_img.image_vul_name = item['image_vul_name']
#                 if single_img.image_desc == "":
#                     single_img.image_desc = item['image_desc']
#                 if single_img.rank != item['rank']:
#                     single_img.rank = item['rank']
#                 if single_img.degree != item['degree']:
#                     single_img.degree = item['degree']
#                 single_img.save()
#             else:
#                 image_info = ImageInfo(image_name=item['image_name'], image_vul_name=item['image_vul_name'],
#                                        image_desc=item['image_desc'], rank=item['rank'], degree=item['degree'],
#                                        is_ok=False, create_date=timezone.now(), update_date=timezone.now())
#                 image_info.save()
#     except Exception as e:
#         pass


def create_share_image_task(image_info, user_info):
    """
    创建共享镜像任务
    :param image_info: 镜像信息
    :param user_info: 用户信息
    :return:
    """
    image_name = image_info.image_name
    user_id = user_info.id
    setting_config = get_setting_config()
    args = {
        "share_username": setting_config["share_username"],
        "image_name": image_name,
        "username": setting_config["username"],
        "pwd": setting_config["pwd"]
    }
    task_info = TaskInfo(task_name="共享镜像："+image_name, user_id=user_id, task_status=1, task_msg=json.dumps({}),
                         task_start_date=timezone.now(), operation_type=5, operation_args=json.dumps(args),
                         create_date=timezone.now(), update_date=timezone.now())
    task_info.save()
    return str(task_info.task_id)


def create_create_image_task(image_info, user_info):
    """
    创建拉取镜像任务
    :param image_info: 镜像信息
    :param user_info: 用户信息
    """
    image_name = image_info.image_name
    if image_name and ":" not in image_name:
        image_name += ":latest"
    user_id = user_info.id
    args = {
        "image_name": image_name,
    }
    task_info = TaskInfo(task_name="拉取镜像：" + image_name, user_id=user_id, task_status=1, task_msg=json.dumps({}),
                         task_start_date=timezone.now(), operation_type=1,
                         operation_args=json.dumps(args), create_date=timezone.now(), update_date=timezone.now())
    task_info.save()
    return str(task_info.task_id)


def create_stop_container_task(container_vul, user_info):
    """
    创建停止容器任务
    :param container_vul: 漏洞容器对象
    :param user_info: 用户信息
    """
    return create_base_container_task(container_vul=container_vul, user_info=user_info, operation_type=3)


def create_delete_container_task(container_vul, user_info):
    """
    创建删除容器任务
    :param container_vul: 漏洞容器对象
    :param user_info: 用户信息
    """
    return create_base_container_task(container_vul=container_vul, user_info=user_info, operation_type=4)


def create_run_container_task(container_vul, user_info):
    """
    创建运行容器任务
    :param container_vul: 漏洞容器对象
    :param user_info: 用户信息
    """
    image_info = container_vul.image_id
    image_name = image_info.image_name
    image_port = image_info.image_port
    user_id = user_info.id
    args = {
        "image_name": image_name,
        "user_id": user_id,
        "image_port": image_port
    }
    task_info = None
    if container_vul.container_status == "running":
        vul_port = container_vul.vul_port
        vul_host = container_vul.vul_host
        task_msg = R.ok(data={"host": vul_host, "port": vul_port, "id": str(container_vul.container_id)})
        task_info = TaskInfo.objects.filter(operation_args=json.dumps(args), task_msg=json.dumps(task_msg),
                                            operation_type=2, task_name="运行容器：" + image_name, user_id=user_id).first()
    if not task_info:
        task_info = TaskInfo.objects.filter(operation_args=json.dumps(args), task_msg="", task_status=1, user_id=user_id,
                                            operation_type=2, task_name="运行容器：" + image_name).first()
    if not task_info:
        task_info = TaskInfo(task_name="运行容器：" + image_name, user_id=user_id, task_status=1,
                             operation_type=2, operation_args=json.dumps(args), task_msg="", create_date=timezone.now(),
                             update_date=timezone.now())
        task_info.save()
    return str(task_info.task_id)


def create_base_container_task(container_vul, user_info, operation_type):
    # 1：拉取镜像 2：创建/启动 容器 3：停止容器 4：删除容器
    task_name_base = ""
    if operation_type == 1:
        task_name_base = "拉取镜像"
    elif operation_type == 2:
        task_name_base = "运行容器"
    elif operation_type == 3:
        task_name_base = "停止容器"
    elif operation_type == 4:
        task_name_base = "删除容器"
    image_info = container_vul.image_id
    image_name = image_info.image_name
    image_port = image_info.image_port
    user_id = user_info.id
    args = {
        "image_name": image_name,
        "user_id": user_id,
        "image_port": image_port,
        "container_id": str(container_vul.container_id)
    }
    task_info = TaskInfo(task_name=task_name_base+"：" + image_name, user_id=user_id, task_status=1,
                         task_start_date=timezone.now(), operation_type=operation_type, task_msg=json.dumps({}),
                         operation_args=json.dumps(args), create_date=timezone.now(), update_date=timezone.now())
    task_info.save()
    return str(task_info.task_id)


def check_container(container_id):
    """
    检测 docker container 是否正常
    :param container_id: container id
    """
    try:
        container = client.containers.get(container_id)
        return {"flag": True, "container": container}
    except NotFound:
        return {"flag": False, "container": None}


def docker_container_run(docker_container, command=""):
    """
    docker 容器启动
    :param docker_container: docker 容器对象
    :param command: 执行命令,默认为空不执行命令
    """
    container_status = str(docker_container.status)
    for i in range(DOCKER_CONTAINER_TIME):
        docker_container.reload()
        container_status = str(docker_container.status)
        if 'running' == container_status:
            if command:
                docker_container.exec_run(command)
            break
        elif 'exited' == container_status:
            pass
        time.sleep(1)
    data = {
        "status": container_status
    }
    if "running" != container_status:
        return R.err(data=data, msg="漏洞容器启动失败")
    else:
        return R.ok(data)


def get_local_ip():
    """
    获取本机IP
    :return: ip
    """
    if VUL_IP:
        return VUL_IP
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    finally:
        if s:
            s.close()
    return local_ip


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

