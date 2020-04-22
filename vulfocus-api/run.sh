#!/bin/bash

service nginx start
wait
python3 manage.py runserver 0.0.0.0:8000