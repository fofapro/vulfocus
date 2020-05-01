#!/usr/bin/env python 
# -*- coding: UTF-8 -*- 
# @Time :2020/4/29 17:42 
# @Author :r4v3zn 
# @Site : 
# @File :serializers.py
from rest_framework import serializers
from user.models import UserProfile
from .models import TaskInfo


class TaskSetSerializer(serializers.ModelSerializer):

    user_name = serializers.SerializerMethodField('get_user_name')
    status_name = serializers.SerializerMethodField("get_status_name")
    operation_type_name = serializers.SerializerMethodField("get_operation_type_name")

    class Meta:
        model = TaskInfo
        fields = ["task_id", "user_name", "task_name", "task_name", "operation_type_name", "operation_args", "task_msg", "create_date", "update_date"]


    def get_operation_type_name(self,obj):
        operation_type = obj.operation_type
        if operation_type == 1:
            return "拉取镜像"
        elif operation_type == 2:
            return "启动容器"
        elif operation_type == 3:
            return "停止容器"
        elif operation_type == 4:
            return "删除容器"


    def status_name(self, obj):
        task_status = obj.task_status
        if task_status == 1:
            return "start"
        elif task_status == 2:
            return "execute"
        elif task_status == 3:
            return "finish"


    def get_user_name(self, obj):
        """
        获取操作用户名
        :param self: self
        :param obj: obj
        """
        user_id = obj.user_id
        user_info = UserProfile.objects.get(id=user_id)
        return user_info.username
