FROM python:3
LABEL maintainer="vulfocus" version="0.3.2.11" description="Vulfocus for Docker"

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

