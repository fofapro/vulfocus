FROM python:3.7-alpine3.15
LABEL maintainer="vulfocus" version="0.3.2.11" description="Vulfocus for Docker"

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories
RUN apk add gcc g++ libzip-dev jpeg-dev libffi-dev freetype-dev

RUN mkdir /vulfocus-api/
WORKDIR /vulfocus-api/
ADD . /vulfocus-api/

ENV VUL_IP=""
ENV EMAIL_HOST=""
ENV EMAIL_HOST_USER=""
ENV EMAIL_HOST_PASSWORD=""
ENV DOCKER_URL="unix://var/run/docker.sock"


RUN python3 -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple some-package -r requirements.txt

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]