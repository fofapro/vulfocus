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
from .common import R, DEFAULT_CONFIG, get_setting_config, get_version_config
from django.db.models import Q
from .models import SysLog, SysConfig, TimeMoudel, TimeTemp, TimeRank
import json
from tasks import tasks
from vulfocus.settings import client, VUL_IP
from tasks.models import TaskInfo
import re
from rest_framework.decorators import api_view, authentication_classes, permission_classes
import datetime
import uuid
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework.pagination import PageNumberPagination
import requests
import time


class MyPageNumberPagination(PageNumberPagination):
    '''
    :分页
    '''
    page_size = 10
    page_size_query_param = "size"
    page_query_param = "page"


def get_request_ip(request):
    """
    获取请求IP
    :param request:
    :return:
    """
    request_ip = ""
    if request.META.get("HTTP_X_REAL_IP"):
        request_ip = request.META.get("HTTP_X_REAL_IP")
    else:
        request_ip = request.META.get("REMOTE_ADDR")
    return request_ip


class CreateTimeTemplate(viewsets.ModelViewSet):

    serializer_class = TimeTempSerializer

    def get_queryset(self, *args, **kwargs):
        return TimeTemp.objects.all()

    def create(self, request, *args, **kwargs):
        """
        创建计时模式模版
        """
        user_id = request.user.id
        time_desc = request.data['desc']
        time_img_type = request.data['time_img_type']
        rank_range = request.data['rank_range']
        name = request.data['name']
        ilist = request.data['ilist']
        template_pattern = request.data['template_pattern']
        existence_name = TimeTemp.objects.filter(name=name).first()
        if ilist:
            ilist = json.dumps(ilist.split(","))
        if existence_name:
            data = {"code": 2001, "message": "名称已存在"}
            return JsonResponse(data=data)
        if not name:
            data = {"code": 2001, "message": "名称不能为空"}
            return JsonResponse(data=data)
        if len(name) > 255:
            data = {"code": 2001, "message": "名称过长"}
            return JsonResponse(data=data)
        if not template_pattern:
            data = {"code": 2001, "message": "计时类型不能为空"}
            return JsonResponse(data=data)
        if request.data['time_range'].isdigit() != True or int(request.data['time_range']) % 30 != 0:
            data = {"code": 2001, "message": "时间范围不能为空，并且必须是整数，且是30的倍数"}
            return JsonResponse(data=data)
        try:
            time_range = request.data['time_range']
        except Exception as e:
            return JsonResponse(data={"code": 2001, "message": "时间范围不能为空"})
        image_type_list = []
        if time_img_type:
            for image_type in time_img_type.split(','):
                image_type = image_type.strip()
                if not image_type:
                    continue
                if image_type in image_type_list:
                    continue
                image_type_list.append(image_type)
        time_img_type = json.dumps(image_type_list)
        img = request.data['imageName']
        timetemp_info = TimeTemp(user_id=user_id, time_range=int(time_range), time_desc=time_desc, image_name=img,
                                 time_img_type=time_img_type, rank_range=rank_range, name=name, image_ids=ilist,
                                 template_pattern=template_pattern)
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


class TimeRankSet(APIView):
    serializer_class = TimeRankSerializer

    def get(self, request):
        user_name = request.user.username
        value = self.request.GET.get("value")
        page = self.request.GET.get("page", 1)
        if page:
            min_size = (int(page) - 1) * 20
            max_size = int(page) * 20
        else:
            min_size = 0
            max_size = 20
        time_data = TimeTemp.objects.all().filter(temp_id=value).first()
        if not time_data:
            time_data = TimeTemp.objects.all().filter(time_desc=value).first()
        count = TimeRank.objects.all().filter(time_temp_id=time_data.temp_id, rank__gt=0).order_by("-rank").count()
        all_temp_data = TimeRank.objects.all().filter(time_temp_id=time_data.temp_id, rank__gt=0).order_by("-rank").all()
        current_rank = 0
        current_score = 0
        for i, _score in enumerate(all_temp_data):
            _score = TimeRankSerializer(_score).data
            if user_name != _score['name']:
                continue
            current_rank = i + 1
            current_score = _score["rank"]
            break
        temp_data = TimeRank.objects.all().filter(time_temp_id=time_data.temp_id, rank__gt=0).order_by("-rank")[min_size:max_size]
        temp_list = []
        for tmp in temp_data:
            temp = TimeRankSerializer(tmp).data
            user_info = UserProfile.objects.filter(username=temp['name']).first()
            avatar = ""
            if user_info:
                avatar = user_info.avatar
            temp['avatar'] = avatar
            temp_list.append(temp)
        return JsonResponse({'results': temp_list, 'count': count, "current_rank": current_rank, 'current_score': current_score })


class TimeMoudelSet(viewsets.ModelViewSet):

    serializer_class = TimeMoudelSerializer

    def get_queryset(self):
        now_time = datetime.datetime.now().timestamp()
        # 更新状态
        TimeMoudel.objects.all().filter(end_time__lt=now_time).update(status=False)
        data = TimeMoudel.objects.all().filter(user_id=self.request.user.id, status=True)
        return data

    @action(methods=["get"], detail=True, url_path="get")
    def get_layout(self, request, pk=None):
        if not pk or pk == "undefined":
            return JsonResponse(R.build(msg="环境不存在"))
        time_info = TimeTemp.objects.filter(temp_id=pk).first()
        time_info.total_view += 1
        time_info.save()
        data = TimeTempSerializer(time_info).data
        return JsonResponse(data)

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
            # print(e)
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
        temp = self.request.GET.get("temp", "")
        rank = self.request.GET.get("rank", "")
        page = self.request.GET.get('page', "")
        min_rank = 0
        try:
            if rank != "undefined" and rank != "":
                rank = float(rank)
                if rank == 0.5:
                    min_rank = 0.0
                if rank == 2.0:
                    min_rank = 1.0
                if rank == 3.5:
                    min_rank = 2.5
                if rank == 5.0:
                    min_rank = 4.0
        except:
            rank = 0.0
        img_t = self.request.GET.get("type", "")
        user = self.request.user
        time_img_type = []
        rank_range = ""
        image_ids = ""
        user_info = UserProfile.objects.filter(username=user.username).first()
        data = TimeMoudel.objects.filter(user_id=self.request.user.id, end_time__gte=now_time).first()
        if data:
            data_temp = TimeTemp.objects.filter(temp_id=data.temp_time_id_id).first()
            if data_temp.image_ids:
                image_ids = json.loads(data_temp.image_ids)
            if data_temp.rank_range != "":
                rank_range = float(data_temp.rank_range)
            try:
                time_img_type = json.loads(data_temp.time_img_type)
            except Exception as e:
                pass
        if user_info.greenhand == True:
            rank_range_greenhand = Q()
            rank_range_greenhand.children.append(('rank__lte', 0.5))
            rank_range_greenhand.children.append(('rank__gte', 0.0))
            return ImageInfo.objects.filter(rank_range_greenhand).order_by('-create_date')
        elif user.is_superuser:
            if query:
                query = query.strip()
                if flag and flag == "flag":
                    image_info_list = ImageInfo.objects.filter(
                        Q(image_name__contains=query) | Q(image_vul_name__contains=query)
                        | Q(image_desc__contains=query)).order_by('-create_date')
                else:
                    query = query.strip()
                    time_img_type_q = Q()
                    if len(time_img_type) > 0:
                        time_img_type_q.connector = 'OR'
                        for img_type in time_img_type:
                            time_img_type_q.children.append(('degree__contains', json.dumps(img_type)))
                    rank_range_q = Q()
                    if rank_range != "":
                        rank_range_q.connector = 'AND'
                        rank_range_q.children.append(('rank__lte', rank_range))
                        rank_range_q.children.append(('rank__gte', min_rank))
                    image_q = Q()
                    image_q.connector = "OR"
                    image_q.children.append(('image_name__contains', query))
                    image_q.children.append(('image_desc__contains', query))
                    image_q.children.append(('image_vul_name__contains', query))
                    query_q = Q()
                    if len(time_img_type_q) > 0:
                        query_q.add(time_img_type_q, 'AND')
                    if type(rank_range) == float:
                        query_q.add(rank_range_q, 'AND')
                    is_ok_q = Q()
                    is_ok_q.connector = 'AND'
                    is_ok_q.children.append(('is_ok', True))
                    query_q.add(is_ok_q, 'AND')
                    if not data:
                        query_q.add(image_q, 'AND')
                    image_info_list = ImageInfo.objects.filter(query_q).order_by('-create_date')
            else:
                if temp == "temp":
                    if rank == 0.0:
                        rank = 5
                    if not img_t:
                        image_info_list = ImageInfo.objects.filter(Q(rank__lte=rank) & Q(rank__gte=min_rank) & Q(is_ok=True)).all()
                    else:
                        img_t_list = img_t.split(",")
                        rank_q = Q()
                        rank_q.connector = "AND"
                        rank_q.children.append(('rank__lte', rank))
                        rank_q.children.append(('rank__gte', min_rank))
                        degree_q = Q()
                        if len(img_t_list) > 0:
                            degree_q.connector = 'OR'
                            for img_type in img_t_list:
                                degree_q.children.append(('degree__contains', json.dumps(img_type)))
                        image_info_list = ImageInfo.objects.filter(~Q(degree="") & rank_q & Q(is_ok=True) & degree_q).all()
                elif flag and flag == "flag":
                    image_info_list = ImageInfo.objects.filter().order_by('-create_date')
                else:
                    time_img_type_q = Q()
                    if len(time_img_type) > 0:
                        time_img_type_q.connector = 'OR'
                        for img_type in time_img_type:
                            time_img_type_q.children.append(('degree__contains', json.dumps(img_type)))
                    rank_range_q = Q()
                    if rank_range != "":
                        rank_range_q.connector = 'AND'
                        rank_range_q.children.append(('rank__lte', rank_range))
                        rank_range_q.children.append(('rank__gte', min_rank))
                    query_q = Q()
                    if len(time_img_type_q) > 0:
                        query_q.add(time_img_type_q, 'AND')
                    if type(rank_range) == float:
                        query_q.add(rank_range_q, 'AND')
                    is_ok_q = Q()
                    is_ok_q.connector = 'AND'
                    is_ok_q.children.append(('is_ok', True))
                    query_q.add(is_ok_q, 'AND')
                    image_info_list = ImageInfo.objects.filter(query_q).order_by('-create_date')
                    if image_ids:
                        imageids_q = Q()
                        imageids_q.connector = 'OR'
                        for img_id in image_ids:
                            imageids_q.children.append(('image_id', img_id))
                        image_info_list = ImageInfo.objects.filter(imageids_q & Q(is_ok=True)).order_by('-create_date')
        else:
            if query:
                query = query.strip()
                time_img_type_q = Q()
                if len(time_img_type) > 0:
                    time_img_type_q.connector = 'OR'
                    for img_type in time_img_type:
                        time_img_type_q.children.append(('degree__contains', json.dumps(img_type)))
                rank_range_q = Q()
                if rank_range != "":
                    rank_range_q.connector = 'AND'
                    rank_range_q.children.append(('rank__lte', rank_range))
                    rank_range_q.children.append(('rank__gte', min_rank))
                image_q = Q()
                image_q.connector = "OR"
                image_q.children.append(('image_name__contains', query))
                image_q.children.append(('image_desc__contains', query))
                image_q.children.append(('image_vul_name__contains', query))
                query_q = Q()
                if len(time_img_type_q) > 0:
                    query_q.add(time_img_type_q, 'AND')
                if type(rank_range) == float:
                    query_q.add(rank_range_q, 'AND')
                is_ok_q = Q()
                is_ok_q.connector = 'AND'
                is_ok_q.children.append(('is_ok', True))
                query_q.add(is_ok_q, 'AND')
                if not data:
                    query_q.add(image_q, 'AND')
                image_info_list = ImageInfo.objects.filter(query_q).order_by('-create_date')
            else:
                if temp == "temp":
                    if rank == 0.0:
                        rank = 5
                    if not img_t:
                        image_info_list = ImageInfo.objects.filter(Q(rank__lte=rank) & Q(rank__gte=min_rank) & Q(is_ok=True)).all()
                    else:
                        img_t_list = img_t.split(",")
                        rank_q = Q()
                        rank_q.connector = 'AND'
                        rank_q.children.append(('rank__lte', rank))
                        rank_q.children.append(('rank__gte', min_rank))
                        degree_q = Q()
                        if len(img_t_list) > 0:
                            degree_q.connector = 'OR'
                            for img_type in img_t_list:
                                degree_q.children.append(('degree__contains', json.dumps(img_type)))
                        image_info_list = ImageInfo.objects.filter(~Q(degree="") & rank_q & Q(is_ok=True) & degree_q).all()
                else:
                    time_img_type_q = Q()
                    if len(time_img_type) > 0:
                        time_img_type_q.connector = 'OR'
                        for img_type in time_img_type:
                            time_img_type_q.children.append(('degree__contains', json.dumps(img_type)))
                    rank_range_q = Q()
                    if rank_range != "":
                        rank_range_q.connector = 'AND'
                        rank_range_q.children.append(('rank__lte', rank_range))
                        rank_range_q.children.append(('rank__gte', min_rank))
                    query_q = Q()
                    if len(time_img_type_q) > 0:
                        query_q.add(time_img_type_q, 'AND')
                    if type(rank_range) == float:
                        query_q.add(rank_range_q, 'AND')
                    is_ok_q = Q()
                    is_ok_q.connector = 'AND'
                    is_ok_q.children.append(('is_ok', True))
                    query_q.add(is_ok_q, 'AND')
                    image_info_list = ImageInfo.objects.filter(query_q).order_by('-create_date')
                    if image_ids:
                        imageids_q = Q()
                        imageids_q.connector = 'OR'
                        for img_id in image_ids:
                            imageids_q.children.append(('image_id', img_id))
                        image_info_list = ImageInfo.objects.filter(imageids_q & Q(is_ok=True)).order_by('-create_date')
        if data and not flag and temp != 'temp':
            for image_info in image_info_list:
                image_info.image_name = ''
                image_info.image_vul_name = ''
                image_info.image_desc = ''

        # pg = MyPageNumberPagination()
        # pglist = pg.paginate_queryset(image_info_list,request=self.request,view=self) # 分页实例
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
        if "is_flag" in data:
            is_flag = data['is_flag']
            image_info.is_flag = is_flag
        if "image_vul_name" in data:
            image_vul_name = data["image_vul_name"]
            image_vul_name = image_vul_name.strip()
            image_info.image_vul_name = image_vul_name
        if "image_desc" in data:
            image_desc = data["image_desc"]
            image_desc = image_desc.strip()
            image_info.image_desc = image_desc
        if "degree" in data:
            degree = data['degree']
            if degree['HoleType']:
                degree['HoleType'] = list(set(degree['HoleType']))
            if degree['devLanguage']:
                degree['devLanguage'] = list(set(degree['devLanguage']))
            if degree['devDatabase']:
                degree['devDatabase'] = list(set(degree['devDatabase']))
            if degree['devClassify']:
                degree['devClassify'] = list(set(degree['devClassify']))
            image_info.degree = json.dumps(degree)
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
        data = request.data

        degree_dict = dict()
        if data['HoleType']:
            degree_dict['HoleType'] = list(set(data['HoleType'].split(',')))
        if data['devLanguage']:
            degree_dict['devLanguage'] = list(set(data['devLanguage'].split(',')))
        if data['devDatabase']:
            degree_dict['devDatabase'] = list(set(data['devDatabase'].split(',')))
        if data['devClassify']:
            degree_dict['devClassify'] = list(set(data['devClassify'].split(',')))
        degree = degree_dict
        try:
            image_rank = request.POST.get("rank", default=2.5)
            image_rank = float(image_rank)
        except:
            image_rank = 2.5
        is_flag = request.POST.get("is_flag", True)
        if is_flag == 'true':
            is_flag = True
        if is_flag == 'false':
            is_flag = False
        image_file = request.FILES.get("file")
        image_info = None
        if image_name:
            if ":" not in image_name:
                image_name += ":latest"
            image_info = ImageInfo.objects.filter(image_name=image_name).first()
        if not image_info:
            image_info = ImageInfo(image_name=image_name, image_vul_name=image_vul_name, image_desc=image_desc,
                                   rank=image_rank, is_ok=False, create_date=timezone.now(), update_date=timezone.now(),
                                   degree=json.dumps(degree), is_flag=is_flag)
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
        if image_info.is_docker_compose == True:
            return JsonResponse(R.build(msg="该镜像为启动方式为docker-compose，不允许直接下载"))
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
        container_vul = ContainerVul.objects.filter(Q(image_id=image_id) & ~Q(container_status='delete') & ~Q(container_status='creat'))
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
        image_info = ImageInfoSerializer(img_info).data
        container_vul = ContainerVul.objects.filter(user_id=user_id, image_id=image_id, time_model_id=time_model_id).first()
        compose_container_vul = ContainerVul.objects.filter(Q(user_id=user_id) & Q(image_id=image_id) &
                                                            Q(time_model_id=time_model_id) & Q(container_status='stop')
                                                            & ~Q(docker_compose_path="")).first()
        if not container_vul or image_info['is_docker_compose'] == True:
            if compose_container_vul:
                container_vul = compose_container_vul
            else:
                container_vul = ContainerVul(image_id=img_info, user_id=user_id, vul_host="", container_status="creat",
                                             docker_container_id="",
                                             vul_port="",
                                             container_port="",
                                             time_model_id=time_model_id,
                                             create_date=django.utils.timezone.now(),
                                             container_flag="")
                container_vul.save()
        if image_info['is_docker_compose'] == True:
            task_id = tasks.start_docker_compose(request, image_id, container_vul, user, get_request_ip(request), time_model_id)
        else:
            task_id = tasks.create_container_task(container_vul, user, get_request_ip(request))
        return JsonResponse(R.ok(task_id))


class DashboardView(APIView):
    serializer_class = ImageInfoSerializer

    def get(self, request):
        now_time = datetime.datetime.now().timestamp()
        query = self.request.GET.get("query", "")
        flag = self.request.GET.get("flag", "")
        temp = self.request.GET.get("temp", "")
        rank = self.request.GET.get("rank", "")
        page = self.request.GET.get('page', "")
        # 获取tab分页标签，用户可以在全部和已启动镜像中进行切换
        activate_name = self.request.GET.get("activate_name", "all")
        image_names = []
        image_info_list = []
        count = 0
        # 表示要返回已启动的镜像
        if activate_name == "started":
            # 取出当前用户所启动的镜像对象
            runnging_containers_image = ContainerVul.objects.filter(Q(user_id=request.user.id) & Q(container_status="running") &
                                                                    ~Q(docker_container_id=""))
            for image in runnging_containers_image:
                image_info = image.image_id
                if image_info:
                    image_names.append(image_info.image_name)
        min_rank = 0
        try:
            if rank != "undefined" and rank != "":
                rank = float(rank)
                if rank == 0.5:
                    min_rank = 0.0
                if rank == 2.0:
                    min_rank = 1.0
                if rank == 3.5:
                    min_rank = 2.5
                if rank == 5.0:
                    min_rank = 4.0
        except:
            rank = 0.0
        if page:
            min_size = (int(page) - 1) * 20
            max_size = int(page) * 20
        else:
            min_size = 0
            max_size = 20
        img_t = self.request.GET.get("type", "")
        user = self.request.user
        degrees = ImageInfo.objects.all().values('degree').distinct()
        HoleType, devLanguage, devDatabase, devClassify = [], [], [], []
        try:
            for single_degree in degrees:
                try:
                    origin_degree = json.loads(single_degree["degree"]) if "degree" in single_degree and single_degree[
                        "degree"] else ""
                except Exception as e:
                    pass
                if isinstance(origin_degree, list):
                    for single_list_degree in origin_degree:
                        single_list_degree.strip()
                        HoleType.append(single_list_degree)
                elif isinstance(origin_degree, dict):
                    if "HoleType" in origin_degree and origin_degree["HoleType"]:
                        current_holetype = list(map(lambda x: x.strip(), origin_degree["HoleType"]))
                        HoleType += current_holetype
                    if "devLanguage" in origin_degree and origin_degree["devLanguage"]:
                        current_devlanguage = list(map(lambda x: x.strip(), origin_degree["devLanguage"]))
                        devLanguage += current_devlanguage
                    if "devDatabase" in origin_degree and origin_degree["devDatabase"]:
                        current_database = list(map(lambda x: x.strip(), origin_degree["devDatabase"]))
                        devDatabase += current_database
                    if "devClassify" in origin_degree and origin_degree["devClassify"]:
                        current_devclassify = list(map(lambda x: x.strip(), origin_degree["devClassify"]))
                        devClassify += current_devclassify
        except Exception as e:
            pass
        return_degree_dict = {"HoleType": list(set(HoleType)), "devLanguage": list(set(devLanguage)),
                              "devDatabase": list(set(devDatabase)), "devClassify": list(set(devClassify))}
        time_img_type = []
        rank_range = ""
        image_ids = ""
        user_info = UserProfile.objects.filter(username=user.username).first()
        data = TimeMoudel.objects.filter(user_id=self.request.user.id, end_time__gte=now_time).first()
        if data:
            data_temp = TimeTemp.objects.filter(temp_id=data.temp_time_id_id).first()
            temp_pattern = data_temp.template_pattern
            if data_temp.image_ids:
                image_ids = json.loads(data_temp.image_ids)
            if data_temp.rank_range != "":
                rank_range = float(data_temp.rank_range)
            try:
                time_img_type = json.loads(data_temp.time_img_type)
            except Exception as e:
                pass
        if user_info.greenhand == True:
            rank_range_greenhand = Q()
            rank_range_greenhand.children.append(('rank__lte', 0.5))
            rank_range_greenhand.children.append(('rank__gte', 0.0))
            count = ImageInfo.objects.filter(rank_range_greenhand, is_ok=True).count()
            if len(image_names) > 0:
                image_info_list = ImageInfo.objects.filter(rank_range_greenhand, is_ok=True,image_name__in=image_names)[min_size:max_size]
            elif len(image_names) == 0 and activate_name == "started":
                pass
            else:
                image_info_list = ImageInfo.objects.filter(rank_range_greenhand, is_ok=True)[min_size:max_size]
        elif user.is_superuser:
            if query:
                query = query.strip()
                if flag and flag == "flag":
                    if len(image_names) > 0:
                        count = ImageInfo.objects.filter(
                            Q(image_name__contains=query) | Q(image_vul_name__contains=query)
                            | Q(image_desc__contains=query) & Q(image_name__in=image_names)).count()
                        image_info_list = ImageInfo.objects.filter(
                            Q(image_name__contains=query) | Q(image_vul_name__contains=query)
                            | Q(image_desc__contains=query) & Q(image_name__in=image_names))[min_size:max_size]
                    elif len(image_names) == 0 and activate_name == "started":
                        pass
                    else:
                        count = ImageInfo.objects.filter(
                            Q(image_name__contains=query) | Q(image_vul_name__contains=query)
                            | Q(image_desc__contains=query)).count()
                        image_info_list = ImageInfo.objects.filter(
                            Q(image_name__contains=query) | Q(image_vul_name__contains=query)
                            | Q(image_desc__contains=query))[min_size:max_size]
                else:
                    query = query.strip()
                    time_img_type_q = Q()
                    if len(time_img_type) > 0:
                        time_img_type_q.connector = 'OR'
                        for img_type in time_img_type:
                            time_img_type_q.children.append(('degree__contains', json.dumps(img_type)))
                    rank_range_q = Q()
                    if rank_range != "":
                        rank_range_q.connector = 'AND'
                        rank_range_q.children.append(('rank__lte', rank_range))
                        rank_range_q.children.append(('rank__gte', min_rank))
                    image_q = Q()
                    image_q.connector = "OR"
                    image_q.children.append(('image_name__contains', query))
                    image_q.children.append(('image_desc__contains', query))
                    image_q.children.append(('image_vul_name__contains', query))
                    query_q = Q()
                    degree_q = Q()
                    degree_q.connector = 'AND'
                    img_t_list = []
                    if img_t != "":
                        img_t_list = img_t.split(",")
                    for img_type in img_t_list:
                        degree_q.children.append(('degree__contains', json.dumps(img_type)))
                    if len(degree_q) > 0:
                        query_q.add(degree_q, 'AND')
                    if len(time_img_type_q) > 0:
                        query_q.add(time_img_type_q, 'AND')
                    if type(rank_range) == float:
                        query_q.add(rank_range_q, 'AND')
                    is_ok_q = Q()
                    is_ok_q.connector = 'AND'
                    is_ok_q.children.append(('is_ok', True))
                    query_q.add(is_ok_q, 'AND')
                    if not data:
                        query_q.add(image_q, 'AND')
                    if len(image_names) > 0:
                        image_info_list = ImageInfo.objects.filter(query_q, image_name__in=image_names)[min_size:max_size]
                    elif len(image_names) == 0 and activate_name == "started":
                        pass
                    else:
                        image_info_list = ImageInfo.objects.filter(query_q)[min_size:max_size]
            else:
                if temp == "temp":
                    if rank == 0.0:
                        rank = 5
                    if not img_t:
                        if len(image_names) > 0:
                            count = ImageInfo.objects.filter(
                                Q(rank__lte=rank) & Q(rank__gte=min_rank) & Q(is_ok=True) &
                                Q(image_name__in=image_names)).all().count()
                            image_info_list = ImageInfo.objects.filter(
                                Q(rank__lte=rank) & Q(rank__gte=min_rank) & Q(is_ok=True) &
                                Q(image_name__in=image_names)).all()[min_size:max_size]
                        elif len(image_names) == 0 and activate_name == "started":
                            pass
                        else:
                            count = ImageInfo.objects.filter(
                                Q(rank__lte=rank) & Q(rank__gte=min_rank) & Q(is_ok=True)).all().count()
                            image_info_list = ImageInfo.objects.filter(
                                Q(rank__lte=rank) & Q(rank__gte=min_rank) & Q(is_ok=True)).all()[min_size:max_size]
                    else:
                        img_t_list = img_t.split(",")
                        rank_q = Q()
                        rank_q.connector = "AND"
                        rank_q.children.append(('rank__lte', rank))
                        rank_q.children.append(('rank__gte', min_rank))
                        degree_q = Q()
                        if len(img_t_list) > 0:
                            degree_q.connector = 'AND'
                            for img_type in img_t_list:
                                degree_q.children.append(('degree__contains', json.dumps(img_type)))
                        if len(image_names) > 0:
                            count = ImageInfo.objects.filter(
                                ~Q(degree="") & rank_q & Q(is_ok=True) & degree_q &
                                Q(image_name__in=image_names)).all().count()
                            image_info_list = ImageInfo.objects.filter(
                                ~Q(degree="") & rank_q & Q(is_ok=True) & degree_q &
                                Q(image_name__in=image_names)).all()[min_size:max_size]
                        elif len(image_names) == 0 and activate_name == "started":
                            pass
                        else:
                            count = ImageInfo.objects.filter(
                                ~Q(degree="") & rank_q & Q(is_ok=True) & degree_q).all().count()
                            image_info_list = ImageInfo.objects.filter(
                                ~Q(degree="") & rank_q & Q(is_ok=True) & degree_q).all()[min_size:max_size]
                elif flag and flag == "flag":
                    if len(image_names) > 0:
                        count = ImageInfo.objects.filter(image_name__in=image_names).count()
                        image_info_list = ImageInfo.objects.filter(image_name__in=image_names)[min_size:max_size]
                    elif len(image_names) == 0 and activate_name == "started":
                        pass
                    else:
                        count = ImageInfo.objects.all().count()
                        image_info_list = ImageInfo.objects.all()[min_size:max_size]
                else:
                    time_img_type_q = Q()
                    if len(time_img_type) > 0:
                        time_img_type_q.connector = 'OR'
                        for img_type in time_img_type:
                            time_img_type_q.children.append(('degree__contains', json.dumps(img_type)))
                    rank_range_q = Q()
                    if rank_range != "":
                        rank_range_q.connector = 'AND'
                        rank_range_q.children.append(('rank__lte', rank_range))
                        rank_range_q.children.append(('rank__gte', min_rank))
                    query_q = Q()
                    if len(time_img_type_q) > 0:
                        query_q.add(time_img_type_q, 'AND')
                    if type(rank_range) == float:
                        query_q.add(rank_range_q, 'AND')
                    is_ok_q = Q()
                    is_ok_q.connector = 'AND'
                    is_ok_q.children.append(('is_ok', True))
                    query_q.add(is_ok_q, 'AND')
                    if len(image_names) > 0:
                        count = ImageInfo.objects.filter(query_q, image_name__in=image_names).count()
                        image_info_list = ImageInfo.objects.filter(query_q, image_name__in=image_names)[min_size:max_size]
                    elif len(image_names) == 0 and activate_name == "started":
                        pass
                    else:
                        count = ImageInfo.objects.filter(query_q).count()
                        image_info_list = ImageInfo.objects.filter(query_q)[min_size:max_size]
                    if image_ids:
                        imageids_q = Q()
                        imageids_q.connector = 'OR'
                        for img_id in image_ids:
                            imageids_q.children.append(('image_id', img_id))
                        if len(image_names) > 0:
                            count = ImageInfo.objects.filter(imageids_q & Q(is_ok=True) &
                                                             Q(image_name__in=image_names)).count()
                            image_info_list = ImageInfo.objects.filter(imageids_q & Q(is_ok=True) &
                                                                       Q(image_name__in=image_names))[min_size:max_size]
                        elif len(image_names) == 0 and activate_name == "started":
                            pass
                        else:
                            count = ImageInfo.objects.filter(imageids_q & Q(is_ok=True)).count()
                            image_info_list = ImageInfo.objects.filter(imageids_q & Q(is_ok=True))[min_size:max_size]
        else:
            if query:
                query = query.strip()
                time_img_type_q = Q()
                if len(time_img_type) > 0:
                    time_img_type_q.connector = 'OR'
                    for img_type in time_img_type:
                        time_img_type_q.children.append(('degree__contains', json.dumps(img_type)))
                rank_range_q = Q()
                if rank_range != "":
                    rank_range_q.connector = 'AND'
                    rank_range_q.children.append(('rank__lte', rank_range))
                    rank_range_q.children.append(('rank__gte', min_rank))
                image_q = Q()
                image_q.connector = "OR"
                image_q.children.append(('image_name__contains', query))
                image_q.children.append(('image_desc__contains', query))
                image_q.children.append(('image_vul_name__contains', query))
                query_q = Q()
                if len(time_img_type_q) > 0:
                    query_q.add(time_img_type_q, 'AND')
                if type(rank_range) == float:
                    query_q.add(rank_range_q, 'AND')
                degree_q = Q()
                img_t_list = []
                if img_t != "":
                    img_t_list = img_t.split(",")
                if len(img_t_list) > 0:
                    degree_q.connector = 'AND'
                    for img_type in img_t_list:
                        degree_q.children.append(('degree__contains', json.dumps(img_type)))
                if len(degree_q) > 0:
                    query_q.add(degree_q, 'AND')
                is_ok_q = Q()
                is_ok_q.connector = 'AND'
                is_ok_q.children.append(('is_ok', True))
                query_q.add(is_ok_q, 'AND')
                if not data:
                    query_q.add(image_q, 'AND')
                if len(image_names) > 0:
                    count = ImageInfo.objects.filter(query_q, image_name__in=image_names).count()
                    image_info_list = ImageInfo.objects.filter(query_q, image_name__in=image_names)[min_size:max_size]
                elif len(image_names) == 0 and activate_name == "started":
                    pass
                else:
                    count = ImageInfo.objects.filter(query_q).count()
                    image_info_list = ImageInfo.objects.filter(query_q)[min_size:max_size]
            else:
                if temp == "temp":
                    if rank == 0.0:
                        rank = 5
                    if not img_t:
                        if len(image_names) > 0:
                            count = ImageInfo.objects.filter(
                                Q(rank__lte=rank) & Q(rank__gte=min_rank) & Q(is_ok=True)
                                & Q(image_name__in=image_names)).all().count()
                            image_info_list = ImageInfo.objects.filter(
                                Q(rank__lte=rank) & Q(rank__gte=min_rank) & Q(is_ok=True)
                                & Q(image_name__in=image_names)).all()[min_size:max_size]
                        elif len(image_names) == 0 and activate_name == "started":
                            pass
                        else:
                            count = ImageInfo.objects.filter(
                                Q(rank__lte=rank) & Q(rank__gte=min_rank) & Q(is_ok=True)).all().count()
                            image_info_list = ImageInfo.objects.filter(
                                Q(rank__lte=rank) & Q(rank__gte=min_rank) & Q(is_ok=True)).all()[min_size:max_size]
                    else:
                        img_t_list = img_t.split(",")
                        rank_q = Q()
                        rank_q.connector = 'AND'
                        rank_q.children.append(('rank__lte', rank))
                        rank_q.children.append(('rank__gte', min_rank))
                        degree_q = Q()
                        if len(img_t_list) > 0:
                            degree_q.connector = 'AND'
                            for img_type in img_t_list:
                                degree_q.children.append(('degree__contains', json.dumps(img_type)))
                        if len(image_names) > 0:
                            count = ImageInfo.objects.filter(
                                ~Q(degree="") & rank_q & Q(is_ok=True) & degree_q
                                & Q(image_name__in=image_names)).all().count()
                            image_info_list = ImageInfo.objects.filter(
                                ~Q(degree="") & rank_q & Q(is_ok=True) & degree_q &
                                Q(image_name__in=image_names)).all()[min_size:max_size]
                        elif len(image_names) == 0 and activate_name == "started":
                            pass
                        else:
                            count = ImageInfo.objects.filter(
                                ~Q(degree="") & rank_q & Q(is_ok=True) & degree_q).all().count()
                            image_info_list = ImageInfo.objects.filter(
                                ~Q(degree="") & rank_q & Q(is_ok=True) & degree_q).all()[min_size:max_size]
                else:
                    time_img_type_q = Q()
                    if len(time_img_type) > 0:
                        time_img_type_q.connector = 'OR'
                        for img_type in time_img_type:
                            time_img_type_q.children.append(('degree__contains', json.dumps(img_type)))
                    rank_range_q = Q()
                    if rank_range != "":
                        rank_range_q.connector = 'AND'
                        rank_range_q.children.append(('rank__lte', rank_range))
                        rank_range_q.children.append(('rank__gte', min_rank))
                    query_q = Q()
                    if len(time_img_type_q) > 0:
                        query_q.add(time_img_type_q, 'AND')
                    if type(rank_range) == float:
                        query_q.add(rank_range_q, 'AND')
                    is_ok_q = Q()
                    is_ok_q.connector = 'AND'
                    is_ok_q.children.append(('is_ok', True))
                    query_q.add(is_ok_q, 'AND')
                    if len(image_names) > 0:
                        count = ImageInfo.objects.filter(query_q, image_name__in=image_names).count()
                        image_info_list = ImageInfo.objects.filter(query_q,
                                                                   image_name__in=image_names)[min_size:max_size]
                    elif len(image_names) == 0 and activate_name == "started":
                        pass
                    else:
                        count = ImageInfo.objects.filter(query_q).count()
                        image_info_list = ImageInfo.objects.filter(query_q)[min_size:max_size]
                    if image_ids:
                        imageids_q = Q()
                        imageids_q.connector = 'OR'
                        for img_id in image_ids:
                            imageids_q.children.append(('image_id', img_id))
                        if len(image_names) > 0:
                            count = ImageInfo.objects.filter(imageids_q & Q(is_ok=True) &
                                                             Q(image_name__in=image_names)).count()
                            image_info_list = ImageInfo.objects.filter(imageids_q & Q(is_ok=True) &
                                                                       Q(image_name__in=image_names))[min_size:max_size]
                        elif len(image_names) == 0 and activate_name == "started":
                            pass
                        else:
                            count = ImageInfo.objects.filter(imageids_q & Q(is_ok=True)).count()
                            image_info_list = ImageInfo.objects.filter(imageids_q & Q(is_ok=True))[min_size:max_size]
        if data and temp_pattern == 1:
            for image_info in image_info_list:
                image_info.image_name = ''
                image_info.image_vul_name = ''
                image_info.image_desc = ''
        data_infos = []
        for imgs in image_info_list:
            img = ImageInfoSerializer(imgs, context={'request': self.request}).data
            if user_info.greenhand != True:
                del img['writeup_date']
                del img['HoleType']
                del img['devLanguage']
                del img['devDatabase']
                del img['devClassify']
                del img['docker_compose_yml']
                del img['docker_compose_env']
                del img['compose_env_port']
                del img['original_yml']
                if img['is_docker_compose'] == True:
                    del img['status']['json_yml']
            else:
                pass
            data_infos.append(img)
        return JsonResponse({'results': data_infos, 'count': count,"degree":return_degree_dict})


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
                container_vul_list = ContainerVul.objects.filter(image_id=image_id,is_docker_compose_correlation=False).order_by('-create_date')
            else:
                container_vul_list = ContainerVul.objects.filter(is_docker_compose_correlation=False).all().order_by('-create_date')
        else:
            container_vul_list = ContainerVul.objects.filter(user_id=user.id, time_model_id=time_model_id, is_docker_compose_correlation=False)
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
        expire = request.GET.get('expire', "")
        image_info = ImageInfo.objects.filter(image_id=container_vul.image_id_id).first()
        if image_info.is_docker_compose == True:
            original_container = ContainerVul.objects.filter(Q(user_id=user_info.id) & Q(image_id=image_info.image_id) &
                                                    Q(container_status="running") & ~Q(docker_compose_path="")).first()
            task_id = tasks.stop_container_task(container_vul=original_container, user_info=user_info,
                                                request_ip=get_request_ip(request))
            return JsonResponse(R.ok(task_id))
        task_id = tasks.stop_container_task(container_vul=container_vul, user_info=user_info,
                                            request_ip=get_request_ip(request))
        setting_config = get_setting_config()
        del_container = setting_config['del_container']
        if expire != "" and expire == "true":
            if not del_container or del_container == 0 or del_container == '0':
                pass
            else:
                tasks.delete_container_task(container_vul=container_vul, user_info=user_info,
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
        user_id = request.user.id
        original_container = ContainerVul.objects.filter(container_id=pk).first()
        # original_container = ContainerVul.objects.filter(Q(user_id=user_id) & Q(container_id=pk)
        #                                                  & ~Q(docker_compose_path="") & ~Q(container_status='delete')).first()
        if not original_container:
            return JsonResponse(R.build(msg="环境不存在"))
        user_info = request.user
        task_id = tasks.delete_container_task(container_vul=original_container, user_info=user_info,
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
                is_compose_container = ContainerVul.objects.filter(user_id=user_id, is_check=True, time_model_id="",
                                                                   image_id=operation_args['image_id']).first()
                img = ImageInfo.objects.filter(image_id=operation_args['image_id']).first()
                if is_compose_container and img.is_docker_compose == True:
                    container_vul.is_check = False
                else:
                    container_vul.is_check = True
                container_vul.save()
                # 检测是否在时间模式中
                now_time = datetime.datetime.now().timestamp()
                time_moudel_data = TimeMoudel.objects.filter(user_id=user_id, end_time__gte=now_time).first()
                if time_moudel_data:
                    rank = 0
                    time_model_id = time_moudel_data.time_id
                    successful = ContainerVul.objects.filter(is_check=True, user_id=user_id, time_model_id=time_model_id).values(
                        'image_id').distinct()
                    rd = TimeRank.objects.filter(time_temp_id=time_moudel_data.temp_time_id_id, user_id=user_id).first()
                    for i in successful:
                        img = ImageInfo.objects.filter(image_id=i['image_id']).first()
                        rank += img.rank
                    if rank >= rd.rank:
                        rd.rank = rank
                        rd.save()
                # 停止 Docker
            tasks.stop_container_task(container_vul=container_vul, user_info=user_info,
                                      request_ip=get_request_ip(request))
            users = UserProfile.objects.filter(id=user_id).first()
            if users.greenhand == True:
                users.greenhand = False
                users.save()
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
def get_writeup_info(request):
    image_id = request.GET.get("id", "")
    writeup_date = ""
    if image_id:
        img_info = ImageInfo.objects.filter(image_id=image_id).first()
        if img_info:
            if img_info.writeup_date:
                writeup_date = json.loads(img_info.writeup_date)
            else:
                writeup_date = ""
        return JsonResponse({'code': 200, 'data': {"username": '', "writeup_date": writeup_date}})
    else:
        return JsonResponse({'code': 200, 'data': {"username": '', "writeup_date": ''}})


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


@api_view(http_method_names=["GET"])
@authentication_classes([])
@permission_classes([])
def get_version(request):
    rsp_data = get_version_config()
    return JsonResponse(R.ok(data=rsp_data))


@api_view(http_method_names=["POST"])
def update_setting(request):
    """
    更新系统配置
    :param request:
    :return:
    """
    user = request.user
    if not user.is_superuser:
        return JsonResponse(R.build(msg="权限不足"))
    username = request.POST.get("username")
    if not username:
        return JsonResponse(R.build(msg="用户名不能为空"))
    pwd = request.POST.get("pwd", DEFAULT_CONFIG["pwd"])
    if not pwd:
        return JsonResponse(R.build(msg="密码不能为空"))
    time = request.POST.get("time")
    share_username = request.POST.get("share_username")
    if not share_username:
        return JsonResponse(R.build(msg="分享用户名不能为空"))
    else:
        share_username_reg = "[\da-zA-z\-]+"
        if not re.match(share_username_reg, share_username):
            return JsonResponse(R.build(msg="分享用户名不符合要求"))
    is_synchronization = request.POST.get("is_synchronization")
    cancel_validation = request.POST.get("cancel_validation")
    cancel_registration = request.POST.get("cancel_registration")
    del_container = request.POST.get("del_container")
    url_name = request.POST.get("url_name")
    if not url_name:
        url_name = 'vulfocus'
    if is_synchronization and 'true' == is_synchronization:
        is_synchronization = 1
    else:
        is_synchronization = 0
    if del_container and 'true' == del_container:
        del_container = 1
    else:
        del_container = 0
    if cancel_validation and 'true' == cancel_validation:
        cancel_validation = 1
    else:
        cancel_validation = 0
    if cancel_registration and 'true' == cancel_registration:
        cancel_registration = 1
    else:
        cancel_registration = 0
    try:
        time = int(time)
        if time != 0 and time < 60:
            time = int(DEFAULT_CONFIG["time"])
    except:
        time = int(DEFAULT_CONFIG["time"])
    with transaction.atomic():
        share_username_config = SysConfig.objects.filter(config_key="share_username").first()
        if not share_username_config:
            username_config = SysConfig(config_key="username", config_value=DEFAULT_CONFIG["username"])
            username_config.save()
        else:
            if share_username_config.config_value != share_username:
                share_username_config.config_value = share_username
                share_username_config.save()
        username_config = SysConfig.objects.filter(config_key="username").first()
        if not username_config:
            username_config = SysConfig(config_key="username", config_value=DEFAULT_CONFIG["username"])
            username_config.save()
        else:
            if username_config.config_value != username:
                username_config.config_value = username
                username_config.save()
        pwd_config = SysConfig.objects.filter(config_key="pwd").first()
        if not pwd_config:
            pwd_config = SysConfig(config_key="pwd", config_value=DEFAULT_CONFIG["pwd"])
            pwd_config.save()
        else:
            if pwd_config.config_value != pwd:
                pwd_config.config_value = pwd
                pwd_config.save()
        time_config = SysConfig.objects.filter(config_key="time").first()
        if not time_config:
            time_config = SysConfig(config_key="time", config_value=DEFAULT_CONFIG["time"])
            time_config.save()
        else:
            if time_config.config_value != str(time):
                time_config.config_value = str(time)
                time_config.save()
        is_synchronization_config = SysConfig.objects.filter(config_key="is_synchronization").first()
        if not is_synchronization_config:
            is_synchronization_config = SysConfig(config_key="is_synchronization", config_value=DEFAULT_CONFIG["time"])
            is_synchronization_config.save()
        else:
            if is_synchronization_config.config_value != str(is_synchronization) or is_synchronization_config.config_value != is_synchronization:
                is_synchronization_config.config_value = str(is_synchronization)
                is_synchronization_config.save()
        del_container_config = SysConfig.objects.filter(config_key="del_container").first()
        if not del_container_config:
            del_container_config = SysConfig(config_key="del_container", config_value=DEFAULT_CONFIG["del_container"])
            del_container_config.save()
        else:
            if del_container_config.config_value != str(del_container) or del_container_config.config_value != del_container:
                del_container_config.config_value = str(del_container)
                del_container_config.save()
        url_name_config = SysConfig.objects.filter(config_key="url_name").first()
        if not url_name_config:
            url_name_config = SysConfig(config_key="url_name", config_value=DEFAULT_CONFIG["url_name"])
            url_name_config.save()
        else:
            if url_name_config.config_value != str(url_name) or url_name_config.config_value != url_name:
                url_name_config.config_value = str(url_name)
                url_name_config.save()
        cancel_validation_config = SysConfig.objects.filter(config_key="cancel_validation").first()
        if not cancel_validation_config:
            cancel_validation_config = SysConfig(config_key="cancel_validation", config_value=DEFAULT_CONFIG["cancel_validation"])
            cancel_validation_config.save()
        else:
            if cancel_validation_config.config_value != str(cancel_validation) or cancel_validation_config.config_value != cancel_validation:
                cancel_validation_config.config_value = str(cancel_validation)
                cancel_validation_config.save()
        cancel_registration_config = SysConfig.objects.filter(config_key="cancel_registration").first()
        if not cancel_registration_config:
            cancel_registration_config = SysConfig(config_key="cancel_registration", config_value=DEFAULT_CONFIG["cancel_registration"])
            cancel_registration_config.save()
        else:
            if cancel_registration_config.config_value != str(cancel_registration) or cancel_registration_config.config_value != cancel_registration:
                cancel_registration_config.config_value = str(cancel_registration)
                cancel_registration_config.save()
    rsp_data = get_setting_config()
    return JsonResponse(R.ok(msg="修改成功", data=rsp_data))


@api_view(http_method_names=["POST"])
def get_timing_imgs(request):
    """
    获取官网镜像信息
    """
    try:
        url = "http://vulfocus.fofa.so/api/imgs/info"
        res = requests.get(url, verify=False).content
        req = json.loads(res)
        image_names = list(ImageInfo.objects.all().values_list('image_name', flat=True))
        for item in req:
            if item['image_name'] == "":
                continue
            if 'is_docker_compose' in item:
                if item['is_docker_compose'] == True:
                    continue
            if item['image_name'] in image_names:
                if item['image_name'] == "vulfocus/vulfocus:latest":
                    continue
                single_img = ImageInfo.objects.filter(image_name__contains=item['image_name']).first()
                if single_img.image_vul_name != item['image_vul_name'] or single_img.image_vul_name == "":
                    single_img.image_vul_name = item['image_vul_name']
                if single_img.image_desc == "":
                    single_img.image_desc = item['image_desc']
                if single_img.rank != item['rank']:
                    single_img.rank = item['rank']
                if single_img.degree != item['degree']:
                    single_img.degree = json.dumps(item['degree'])
                if "writeup_date" in item and single_img.writeup_date != item['writeup_date']:
                    single_img.writeup_date = item['writeup_date']
                single_img.save()
            else:
                if "writeup_date" in item:
                    writeup_date = item['writeup_date']
                else:
                    writeup_date = ""
                image_info = ImageInfo(image_name=item['image_name'], image_vul_name=item['image_vul_name'],
                                       image_desc=item['image_desc'], rank=item['rank'], degree=json.dumps(item['degree']),
                                       is_ok=False, create_date=timezone.now(), writeup_date=writeup_date,
                                       update_date=timezone.now())
                image_info.save()
        return JsonResponse({"code": 200, "data": "成功"})
    except Exception as e:
        return JsonResponse({"code": 201, "data": e})


@api_view(http_method_names=["POST"])
def update_enterprise_setting(request):
    user = request.user
    if not user.is_superuser:
        return JsonResponse(R.build(msg="权限不足"))
    url_name = request.POST.get("url_name")
    enterprise_bg = request.POST.get("enterprise_bg", "")
    enterprise_logo = request.POST.get("enterprise_logo", "")
    if not url_name:
        url_name = 'vulfocus'
    try:
        with transaction.atomic():
            url_name_config = SysConfig.objects.filter(config_key="url_name").first()
            if not url_name_config:
                url_name_config = SysConfig(config_key="url_name", config_value=DEFAULT_CONFIG["url_name"])
                url_name_config.save()
            else:
                if url_name_config.config_value != str(
                        url_name) or url_name_config.config_value != url_name:
                    url_name_config.config_value = str(url_name)
                    url_name_config.save()
            enterprise_bg_config = SysConfig.objects.filter(config_key="enterprise_bg").first()
            if not enterprise_bg_config:
                enterprise_bg_config = SysConfig(config_key="enterprise_bg", config_value=DEFAULT_CONFIG["enterprise_bg"])
                enterprise_bg_config.save()
            else:
                if enterprise_bg_config.config_value != str(
                        enterprise_bg) or enterprise_bg_config.config_value != enterprise_bg:
                    enterprise_bg_config.config_value = str(enterprise_bg)
                    enterprise_bg_config.save()
            enterprise_logo_config = SysConfig.objects.filter(config_key="enterprise_logo").first()
            if not enterprise_logo_config:
                enterprise_logo_config = SysConfig(config_key="enterprise_logo", config_value=DEFAULT_CONFIG["enterprise_logo"])
                enterprise_logo_config.save()
            else:
                if enterprise_logo_config.config_value != str(
                        enterprise_logo) or enterprise_logo_config.config_value != enterprise_logo:
                    enterprise_logo_config.config_value = str(enterprise_logo)
                    enterprise_logo_config.save()
    except:
        return JsonResponse(R.build('修改失败'))
    rsp_data = get_setting_config()
    return JsonResponse(R.ok(msg="修改成功", data=rsp_data))


class UserRank(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        return UserProfile.objects.all().order_by("rank")


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


@csrf_exempt
def get_img_info(req):
    if req.method == "GET":
        imgs = ImageInfo.objects.filter(is_docker_compose=False).all().values("image_name", "image_vul_name", "image_desc", "rank", "degree", "writeup_date")
        imglist = list()
        for i in imgs:
            degree = []
            try:
                degree = json.loads(i['degree'])
            except Exception as e:
                pass
            i['degree']=degree
            imglist.append(i)
        return JsonResponse(imglist, safe=False)


@csrf_exempt
def get_url_name(req):
    if req.method == "GET":
        configs = get_setting_config()
        try:
            url_name = configs['url_name']
        except:
            url_name = "vulfocus"
        return JsonResponse(url_name, safe=False)


@csrf_exempt
def get_setting_img(req):
    if req.method == "GET":
        rsp_data = {}
        try:
            set_data = get_setting_config()
            if set_data:
                rsp_data['enterprise_logo'] = set_data['enterprise_logo']
                rsp_data['enterprise_bg'] = set_data['enterprise_bg']
                rsp_data['cancel_registration'] = set_data['cancel_registration']
        except:
            rsp_data = {}
        return JsonResponse(R.ok(data=rsp_data))


@api_view(http_method_names=["GET"])
def get_container_status(request):
    container_id = request.GET.get("container_id", "")
    current_container = ContainerVul.objects.filter(container_id=container_id).first()
    if not current_container:
        return JsonResponse({"code": 400, "msg": "容器不存在"})
    return JsonResponse({"code": 200, "status": current_container.container_status})


@csrf_exempt
def get_operation_image_api(req):
    '''
    开放api（官网）
    '''

    # 返回所有数据
    if req.method == "GET":
        # 获取认证的licence
        licence = req.GET.get("licence", "")
        # 获取用户名
        username = req.GET.get("username", "")
        # 判断用户是否存在
        if username:
            user = UserProfile.objects.filter(username=username).first()
            if not user:
                return HttpResponse(json.dumps(R.err(msg="认证信息错误"), ensure_ascii=False))
        else:
            return HttpResponse(json.dumps(R.err(msg="认证信息错误"), ensure_ascii=False))
        # 判断licence是否匹配用户，符合则返回所有已下载的镜像数据
        if licence and licence == user.licence:
            imgs = ImageInfo.objects.filter(is_ok=True).all().values("image_name", "image_vul_name", "image_desc")
            imglist = list()
            for i in imgs:
                imglist.append(i)
            return HttpResponse(json.dumps(R.ok(data=imglist), ensure_ascii=False), content_type='application/json')
        else:
            return HttpResponse(json.dumps(R.err(msg="认证信息错误"), ensure_ascii=False))

    # 启动镜像
    if req.method == "POST":
        # 获取请求参数，image_name镜像名称全称+版本号，licence用于用户认证，username用户名称
        image_name = req.POST.get("image_name", "")
        licence = req.POST.get("licence", "")
        username = req.POST.get("username", "")
        requisition = req.POST.get("requisition", "")
        # 判断用户是否存在
        if username:
            user = UserProfile.objects.filter(username=username).first()
            if not user:
                return HttpResponse(json.dumps(R.err(msg="认证信息错误"), ensure_ascii=False))
        else:
            return HttpResponse(json.dumps(R.err(msg="认证信息错误"), ensure_ascii=False))
        # 判断licence是否匹配用户
        if licence and licence == user.licence:
            pass
        else:
            return HttpResponse(json.dumps(R.err(msg="认证信息错误"), ensure_ascii=False))
        # 判断镜像是否存在
        if image_name:
            image = ImageInfo.objects.filter(image_name=image_name, is_ok=True).first()
            if not image:
                return HttpResponse(json.dumps(R.err(msg="镜像不存在"), ensure_ascii=False))
        else:
            return HttpResponse(json.dumps(R.err(msg="镜像名称不能为空"), ensure_ascii=False))
        if not requisition:
            return HttpResponse(json.dumps(R.err(msg="错误的请求"), ensure_ascii=False))
        if requisition and requisition not in ['start', 'stop', 'delete']:
            return HttpResponse(json.dumps(R.err(msg="错误的请求"), ensure_ascii=False))
        # 启动惊喜那个的请求
        if requisition == "start":
            data_count = ContainerVul.objects.filter(user_id=user.id, container_status='running').all().count()
            data_start = ContainerVul.objects.filter(user_id=user.id, image_id=image.image_id, container_status='running').first()
            if data_start:
                status = dict()
                try:
                    HTTP_HOST = req.META.get("HTTP_REFERER")
                    if HTTP_HOST.count(":") == 2:
                        status["host"] = data_start.vul_host
                    else:
                        if HTTP_HOST:
                            HTTP_HOST = HTTP_HOST.replace("http://", "").replace("https://", "")
                            origin_host = data_start.vul_host.split(":")
                            if len(origin_host) >= 2:
                                status["host"] = HTTP_HOST[:-1] + ":" + origin_host[1]
                        else:
                            status["host"] = data_start.vul_host
                except:
                    status["host"] = data_start.vul_host
                status["port"] = data_start.vul_port
                return HttpResponse(json.dumps(R.ok(data=status, msg="镜像已启动"), ensure_ascii=False))
            if data_count > 3:
                return HttpResponse(json.dumps(R.err(msg="同时启动容器数量达到上线"), ensure_ascii=False))
            img_info = image
            # 当前用户id
            image_id = img_info.image_id
            user_id = user.id
            now_time = datetime.datetime.now().timestamp()
            time_moudel_data = TimeMoudel.objects.filter(user_id=user_id, end_time__gte=now_time).first()
            time_model_id = ''
            if time_moudel_data:
                time_model_id = time_moudel_data.time_id
            image_info = ImageInfoSerializer(img_info).data
            container_vul = ContainerVul.objects.filter(user_id=user_id, image_id=image_id,
                                                        time_model_id=time_model_id, container_status='stop').first()
            compose_container_vul = ContainerVul.objects.filter(Q(user_id=user_id) & Q(image_id=image_id) &
                                                                Q(time_model_id=time_model_id) & Q(
                                                                 container_status='stop') & ~Q(docker_compose_path="")).first()
            if not container_vul or image_info['is_docker_compose'] == True:
                if compose_container_vul:
                    container_vul = compose_container_vul
                else:
                    container_vul = ContainerVul(image_id=img_info, user_id=user_id, vul_host="",
                                                 container_status="creat",
                                                 docker_container_id="",
                                                 vul_port="",
                                                 container_port="",
                                                 time_model_id=time_model_id,
                                                 create_date=django.utils.timezone.now(),
                                                 container_flag="")
                    container_vul.save()
            if image_info['is_docker_compose'] == True:
                task_id = tasks.start_docker_compose(req, image_id, container_vul, user,
                                                     get_request_ip(req), time_model_id)
            else:
                task_id = tasks.create_container_task(container_vul, user, get_request_ip(req))
            task_info = TaskInfo.objects.filter(task_id=task_id)
            status = dict()
            num = 0
            while True:
                num += 1
                time.sleep(3)
                data = ContainerVul.objects.filter(user_id=user_id, image_id=image_id, container_status='running').first()
                if data:
                    try:
                        HTTP_HOST = req.META.get("HTTP_REFERER")
                        if HTTP_HOST.count(":") == 2:
                            status["host"] = data.vul_host
                        else:
                            if HTTP_HOST:
                                HTTP_HOST = HTTP_HOST.replace("http://", "").replace("https://", "")
                                origin_host = data.vul_host.split(":")
                                if len(origin_host) >= 2:
                                    status["host"] = HTTP_HOST[:-1] + ":" + origin_host[1]
                            else:
                                status["host"] = data.vul_host
                    except:
                        status["host"] = data.vul_host
                    status["port"] = data.vul_port
                    return HttpResponse(json.dumps(R.ok(data=status, msg="启动成功"), ensure_ascii=False))
                else:
                    if num == 3:
                        break
            return HttpResponse(json.dumps(R.err(msg="启动失败"), ensure_ascii=False))
        # 停止镜像的请求
        if requisition == "stop":
            container_vul = ContainerVul.objects.filter(image_id=image.image_id, user_id=user.id,
                                                        container_status="running").first()
            if not container_vul:
                return HttpResponse(json.dumps(R.err(msg="镜像已经停止"), ensure_ascii=False))
            if image.is_docker_compose == True:
                original_container = ContainerVul.objects.filter(
                    Q(user_id=user.id) & Q(image_id=image.image_id) &
                    Q(container_status="running") & ~Q(docker_compose_path="")).first()
                if not original_container:
                    return HttpResponse(json.dumps(R.err(msg="镜像已经停止"), ensure_ascii=False))
                task_id = tasks.stop_container_task(container_vul=original_container, user_info=user,
                                                    request_ip=get_request_ip(req))
                return HttpResponse(json.dumps(R.ok(msg="停止成功"), ensure_ascii=False))
            else:
                task_id = tasks.stop_container_task(container_vul=container_vul, user_info=user,
                                                    request_ip=get_request_ip(req))
                return HttpResponse(json.dumps(R.ok(msg="停止成功"), ensure_ascii=False))
        # 删除镜像的请求
        if requisition == "delete":
            container_status_q = Q()
            container_status_q.connector = "OR"
            container_status_q.children.append(('container_status', "running"))
            container_status_q.children.append(('container_status', "stop"))
            container_vul = ContainerVul.objects.filter(Q(image_id=image.image_id) & Q(user_id=user.id) & Q(container_status_q)).first()
            if not container_vul:
                return HttpResponse(json.dumps(R.err(msg="镜像已经删除"), ensure_ascii=False))
            if image.is_docker_compose == True:
                original_container = ContainerVul.objects.filter(
                    Q(user_id=user.id) & Q(image_id=image.image_id) & ~Q(docker_compose_path="") & Q(container_status_q)).first()
                if not original_container:
                    return HttpResponse(json.dumps(R.err(msg="镜像已经删除"), ensure_ascii=False))
                task_id = tasks.delete_container_task(container_vul=original_container, user_info=user,
                                                        request_ip=get_request_ip(req))
                return HttpResponse(json.dumps(R.ok(msg="删除成功"), ensure_ascii=False))
            else:
                task_id = tasks.delete_container_task(container_vul=container_vul, user_info=user,
                                                        request_ip=get_request_ip(req))

                return HttpResponse(json.dumps(R.ok(msg="删除成功"), ensure_ascii=False))