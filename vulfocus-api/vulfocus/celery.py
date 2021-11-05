#!/usr/bin/env python 
# -*- coding: UTF-8 -*- 
# @Time :2020/4/27 20:21 
# @Author :r4v3zn 
# @Site : 
# @File :celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vulfocus.settings")

app = Celery("vulfocus")

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


app.conf.update(
    CELERYBEAT_SCHEDULE={
        'update_images': {
            'task': 'tasks.update_images',
            'schedule':  timedelta(minutes=60),
        },
        'check_images': {
            'task': 'tasks.check_images',
            'schedule':  timedelta(minutes=10),
        },
        'download_images': {
            'task': 'tasks.download_images',
            'schedule':  timedelta(hours=1),
        },
        'duplicate': {
            'task': 'tasks.duplicate',
            'schedule': timedelta(minutes=10),
        }
    }
)