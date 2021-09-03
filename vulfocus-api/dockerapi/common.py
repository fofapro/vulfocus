#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/28 11:15 PM
# @Author  : woo0nise
# @Site    :
# @File    : common.py
# @Software: PyCharm
from vulfocus.settings import client
from .models import SysConfig


HTTP_OK = 200
HTTP_OK_RUNNING = 1001
HTTP_ERR = 500
HTTP_BULD = 201

DEFAULT_CONFIG = {
    "share_username": "",
    "username": "vulshare",
    "pwd": "2a295233-801b-4efb-9f78-916330b984f6",
    "time": 30 * 60,
    "is_synchronization": 0,
    "del_container": 1,
    'cancel_validation': 1,
    'cancel_registration': 1,
    "version":"v0.3.2.7",
    "url_name": "vulfocus",
    "enterprise_bg": "",
    "enterprise_logo": ""
}

def get_version_config():
    rsp_data = {}
    config_key = "version"
    config = SysConfig.objects.filter(config_key=config_key).first()
    config_value = DEFAULT_CONFIG[config_key]
    if not config:
        config = SysConfig(config_key=config_key, config_value=config_value)
        config.save()
    config.config_value = config_value
    config.save()
    config_key = config.config_key
    config_value = config.config_value
    rsp_data[config_key] = config_value
    return rsp_data


def docker_login(username, pwd):
    try:
        client.login(username=username, password=pwd)
        return True
    except:
        return False


def get_setting_config():
    """
    获取配置信息
    """
    rsp_data = {}
    for config_key in DEFAULT_CONFIG:
        config = SysConfig.objects.filter(config_key=config_key).first()
        config_value = DEFAULT_CONFIG[config_key]
        if not config:
            config = SysConfig(config_key=config_key, config_value=config_value)
            config.save()
        config_key = config.config_key
        config_value = config.config_value
        if config_key == 'is_synchronization':
            if config_value == 1 or config_value == '1':
                config_value = True
            else:
                config_value = False
        if config_key == 'del_container':
            if config_value == 1 or config_value == '1':
                config_value = True
            else:
                config_value = False
        if config_key == 'cancel_validation':
            if config_value == 1 or config_value == '1':
                config_value = True
            else:
                config_value = False
        if config_key == 'cancel_registration':
            if config_value == 1 or config_value == '1':
                config_value = True
            else:
                config_value = False
        rsp_data[config_key] = config_value
    return rsp_data


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

    @staticmethod
    def running(data=None, msg=''):
        return {
            "data": data,
            "status": HTTP_OK_RUNNING,
            "msg": msg
        }