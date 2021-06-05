#!/bin/bash

service nginx start
wait
service redis-server restart
wait
nohup python3 manage.py runserver 0.0.0.0:8000 &
celery -B -A vulfocus worker -l info -E --logfile=celery.log

