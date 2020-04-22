#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/28 11:15 PM
# @Author  : woo0nise
# @Site    :
# @File    : common.py
# @Software: PyCharm

HTTP_OK = 200
HTTP_ERR = 500
HTTP_BULD = 201


class R:

    @staticmethod
    def ok(data=None, msg='OK'):
        return {
            "data": data,
            "status": HTTP_OK,
            "msg": msg
        }

    @staticmethod
    def err(data=None, msg='服务器内部错误'):
        return {
            "data": data,
            "status": HTTP_ERR,
            "msg": msg
        }

    @staticmethod
    def build(data=None, msg=''):
        return {
            "data": data,
            "status": HTTP_BULD,
            "msg": msg
        }
