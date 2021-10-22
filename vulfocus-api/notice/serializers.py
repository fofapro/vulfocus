#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： xuzhiyi
# datetime： 2021/9/3 14:06
# ide： PyCharm


from rest_framework import serializers
from .models import Notice
import json
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["unread", "target_object_id", "recipient"]


class NoticeInfoSerializer(serializers.ModelSerializer):
    create_date = serializers.SerializerMethodField("transition_create_time")
    update_date = serializers.SerializerMethodField("transition_update_time")
    notice_content = serializers.SerializerMethodField("transition_content")
    title = serializers.SerializerMethodField("title_check")
    notification = serializers.SerializerMethodField("get_notification")

    def transition_create_time(self,obj):
        return obj.create_date.strftime("%Y-%m-%d %H:%M:%S")

    def transition_update_time(self,obj):
        return obj.update_date.strftime("%Y-%m-%d %H:%M:%S")

    def transition_content(self,obj):
        content = obj.notice_content
        try:
            return json.loads(content)
        except Exception as e:
            return ""

    def title_check(self,obj):
        title = obj.title
        return title

    def get_notification(self, obj):
        user = self.context["request"].user
        notice_id = obj.notice_id
        notification = Notification.objects.filter(target_object_id=notice_id, recipient=user).only("unread","target_object_id").first()
        try:
            return NotificationSerializer(notification).data
        except Exception as e:
            return ""


    class Meta:
        model = Notice
        fields = "__all__"
