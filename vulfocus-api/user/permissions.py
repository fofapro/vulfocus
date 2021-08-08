#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： xuzhiyi
# datetime： 2021/7/16 10:17 
# ide： PyCharm


#自定义用户权限

from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.username==obj.username
