import uuid

import docker
from django.db.models import Q
import traceback
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.response import Response
from dockerapi.common import R
from network.models import NetWorkInfo
from network.serializers import NetWorkInfoSerializer
from vulfocus.settings import client
from layout_image.models import LayoutServiceNetwork


class NetWorkInfoViewSet(viewsets.ModelViewSet):
    """
    网关ViewSet
    """
    serializer_class = NetWorkInfoSerializer

    def get_queryset(self):
        request = self.request
        user = request.user
        query = self.request.GET.get("query", "")
        if user.is_superuser:
            return NetWorkInfo.objects.filter(Q(net_work_name__contains=query) | Q(net_work_subnet__contains=query) |
                                       Q(net_work_gateway__contains=query)).order_by('-create_date')
        else:
            return []

    def create(self, request, *args, **kwargs):
        data_dict = request.data
        user_id = request.user.id
        try:
            net_work_name = data_dict['net_work_name']
            network_list = client.networks.list()
            for network in network_list:
                if network.name == net_work_name:
                    return JsonResponse(R.err(msg="服务器中已经有同名网卡存在"))
        except Exception as e:
            return Response(R.build(msg="网卡名称不能为空"))
        try:
            net_work_subnet = data_dict['net_work_subnet']
        except Exception as e:
            return Response(R.build(msg="子网不能为空"))
        try:
            net_work_gateway = data_dict['net_work_gateway']
        except Exception as e:
            return Response(R.build(msg="网关不能为空"))
        try:
            net_work_scope = data_dict['net_work_scope']
        except Exception as e:
            net_work_scope = 'local'
        try:
            net_work_driver = data_dict['net_work_driver']
        except Exception as e:
            net_work_driver = 'bridge'
        try:
            enable_ipv6 = data_dict['enable_ipv6']
        except Exception as e:
            enable_ipv6 = False
        try:
            rs = NetWorkInfo.objects.filter(net_work_name=net_work_name)
            if len(rs) > 0:
                return Response(R.build(msg="网卡名称不能重复"))
            rs = NetWorkInfo.objects.filter(net_work_subnet=net_work_subnet)
            if len(rs) > 0:
                return Response(R.build(msg="子网不能重复"))
            rs = NetWorkInfo.objects.filter(net_work_gateway=net_work_gateway)
            if len(rs) > 0:
                return Response(R.build(msg="网关不能重复"))
        except Exception as e:
            print(e)
        if not net_work_subnet:
            network_list = client.networks.list()
            for network in network_list:
                network_configs = network.attrs['IPAM']['Config']
                if len(network_configs) > 0:
                    subnet = network_configs[0]['Subnet']
                    net_work_gateway = network_configs[0]['Gateway']
                    if subnet != net_work_subnet:
                        continue
                    net_work_client_id = network.attrs["Id"]
                    net_work_scope = network.attrs["Scope"]
                    net_work_driver = network.attrs["Driver"]
                    enable_ipv6 = network.attrs["EnableIPv6"]
                    break
        else:
            if net_work_subnet == "192.168.10.10/24":
                return JsonResponse(R.err(msg="该网段已在服务器内部使用，请更换网段"))
            if net_work_gateway == "192.168.10.10":
                return JsonResponse(R.err(msg="该网关已在服务器内部使用，请更换网关"))
            try:
                ipam_pool = docker.types.IPAMPool(
                    subnet=net_work_subnet,
                    gateway=net_work_gateway
                )
                ipam_config = docker.types.IPAMConfig(
                    pool_configs=[ipam_pool]
                )
                if not net_work_name:
                    return JsonResponse(R.err(msg="网卡名称不能为空"))
                try:
                    net_work = client.networks.create(
                        net_work_name,
                        driver=net_work_driver,
                        ipam=ipam_config,
                        scope=net_work_scope
                    )
                except Exception as e:
                    return JsonResponse(R.err(msg="子网或者网关设置错误"))
                net_work_client_id = str(net_work.id)
                if not net_work_gateway:
                    net_work_gateway = net_work.attrs['IPAM']['Config']['Gateway']
            except Exception as e:
                traceback.print_exc()
                return JsonResponse(R.err(msg="服务器内部错误"))
        network_info = NetWorkInfo(net_work_id=str(uuid.uuid4()), net_work_client_id=net_work_client_id, create_user=user_id,
                                    net_work_name=net_work_name, net_work_driver=net_work_driver, net_work_subnet=net_work_subnet,
                                    net_work_gateway=net_work_gateway, net_work_scope=net_work_scope, enable_ipv6=enable_ipv6)
        network_info.save()
        data = NetWorkInfoSerializer(network_info).data
        return JsonResponse(R.ok(data=data))

    def destroy(self, request, *args, **kwargs):
        """
        删除镜像信息
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user = request.user
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足"))
        network = self.get_object()
        count = LayoutServiceNetwork.objects.filter(network_id=network).count()
        if count == 0:
            try:
                docker_network = client.networks.get(network.net_work_client_id)
                docker_network.remove()
            except Exception as e:
                try:
                    network_list = client.networks.list()
                    for network in network_list:
                        network_configs = network.attrs['IPAM']['Config']
                        if len(network_configs) > 0:
                            subnet = network_configs[0]['Subnet']
                            if subnet != network.net_work_subnet:
                                continue
                            network.remove()
                except Exception as e:
                        pass
            network.delete()
            return JsonResponse(R.ok())
        else:
            return JsonResponse(R.build(msg="网卡 %s 正在使用无法删除" % (network.net_work_subnet,)))
