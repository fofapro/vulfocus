#!/usr/bin/env python 
# -*- coding: UTF-8 -*- 
# @Time :2020/4/27 20:21 
# @Author :r4v3zn 
# @Site : 
# @File :celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vulfocus.settings")

app = Celery("vulfocus")

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
