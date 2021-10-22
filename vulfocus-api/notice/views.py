from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse
from notifications.signals import notify
from notice.models import Notice
from notifications.models import Notification
from .serializers import NoticeInfoSerializer
from dockerapi.common import R
from user.models import UserProfile
from rest_framework import viewsets
from django.core.paginator import Paginator
import requests
import json
import datetime
import uuid
# Create your views here.


@api_view(http_method_names=["GET"])
def get_notifications_count(request):
    """
    获取当前用户未读通知数量
    :param request:
    :return:
    """
    user = request.user
    notifications_count = user.notifications.unread().count()
    results = []
    for _data in user.notifications.unread():
        if _data.recipient == request.user:
            results.append(Notice.objects.filter(notice_id=_data.target_object_id).first().title)
    return JsonResponse({"notifications_count": notifications_count,"results":results})


@api_view(http_method_names=["GET"])
def get_public_notice(request):
    notices = []
    all_notices = Notice.objects.filter(is_public=True)
    for single_notice in all_notices:
        notices.append(single_notice)
    notices.sort(key=lambda item: item.update_date, reverse=True)
    page_no = int(request.GET.get("page", "1"))
    pages = Paginator(notices, 20)
    page = pages.page(page_no)
    results = []
    for _data in page:
        results.append(_data)
    data = {
        "results": NoticeInfoSerializer(results, many=True, context={'request': request}).data,
        "count": len(notices)
    }
    return JsonResponse(R.ok(data=data))


@api_view(http_method_names=["GET"])
def notice_detail(request):
    notice_id = request.GET.get("notice_id", "")
    if not notice_id:
        return JsonResponse({"code": 400, "msg": "公告不存在"})
    notice = Notice.objects.filter(notice_id=notice_id).first()
    if not notice:
        return JsonResponse({"code": 400, "msg": "公告不存在"})
    notification = Notification.objects.filter(target_object_id=notice_id, recipient=request.user).first()
    if notification:
        notification.mark_as_read()
    return JsonResponse({"code": 200, "data": json.loads(notice.notice_content), "title":notice.title})


class NoticeViewset(viewsets.ModelViewSet):
    serializer_class = NoticeInfoSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_superuser:
            return JsonResponse(R.build("权限不足"))
        query = self.request.GET.get("query", "")
        if query:
            query = query.strip()
            seven_days_ago = datetime.datetime.now()-datetime.timedelta(days=7)
            nots = Notice.objects.filter(title__contains=query).all()
            for single_not in nots:
                if single_not.update_date < seven_days_ago:
                    single_not.is_newest = False
            return nots
        else:
            seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
            nots = Notice.objects.all()
            for single_not in nots:
                if single_not.update_date < seven_days_ago:
                    single_not.is_newest = False
            return nots

    def create(self, request, *args, **kwargs):
        user = request.user
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足"))
        now_time = datetime.datetime.now()
        data = request.data
        notice_data = data['notice_content']
        title = data["title"]
        if not notice_data:
            return JsonResponse({"code": 400, "message": "公告内容不能为空"})
        if not title:
            return JsonResponse({"code": 400, "message": "公告标题不能为空"})
        if "update_notice" in data and data["update_notice"] == True:
            notice_id = data['notice_id']
            update_noticeinfo = Notice.objects.filter(notice_id=notice_id, is_public=False).first()
            update_noticeinfo.update_date = now_time
            update_noticeinfo.notice_content = json.dumps(notice_data)
            update_noticeinfo.title = title
            update_noticeinfo.save()
            return JsonResponse({"code": 200, "msg": "公告修改成功"})
        else:
            notice_info = Notice(notice_id=str(uuid.uuid4()), title=title, notice_content=json.dumps(notice_data),
                                 create_date=now_time)
            notice_info.save()
        return JsonResponse({"code": 200, "msg": "提交成功"})

    def destroy(self, request, *args, **kwargs):
        user = request.user
        if not user.is_superuser:
            return JsonResponse(R.build("权限不足"))
        if "id" in request.data:
            notice_id = request.data["id"]
        else:
            notice = self.get_object()
            notice_id = notice.notice_id
        if notice_id:
            notice_instance = Notice.objects.filter(notice_id=notice_id).first()
            notice_instance.delete()
            notifications = Notification.objects.all()
            for single_notification in notifications:
                if single_notification.target_object_id ==notice_id:
                    single_notification.delete()
            return JsonResponse({"code": 200, "message": "删除成功"})
        return JsonResponse({"code": 400, "message": "删除失败"})


@api_view(http_method_names=["POST"])
def publish_notice(request):
    user = request.user
    if not user.is_superuser:
        return JsonResponse(R.build("权限不足"))
    if "id" in request.data:
        try:
            notice_info = Notice.objects.filter(notice_id=request.data["id"]).first()
            notice_info.is_public = True
            notice_info.is_newest = True
            notice_info.save()
            notify.send(request.user,
                        recipient=UserProfile.objects.all(),
                        verb="public notice", target=notice_info)
            return JsonResponse({"code": 200, "message": "发布成功"})
        except Exception as e:
            return JsonResponse({"code": 400, "message": "发布失败"})
    return JsonResponse({"code": 400, "message": "发布失败"})


@api_view(http_method_names=["GET"])
def get_content(request):
    notice_id = request.GET.get("notice_id","")
    print(notice_id)
    if not notice_id:
        return JsonResponse({"code": 400, "msg": "公告不存在"})
    notice_instance = Notice.objects.filter(notice_id=notice_id).first()
    return JsonResponse({"code": 200, "content": json.loads(notice_instance.notice_content)})


