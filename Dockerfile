FROM python:3
LABEL maintainer="r4v3zn <woo0nise@gmail.com>" version="0.1.0" description="Vulfocus for Docker"
EXPOSE 80
RUN mkdir /vulfocus-api/
WORKDIR /vulfocus-api/
ADD vulfocus-api/ /vulfocus-api/
ENV VUL_IP=""
RUN mv /etc/apt/sources.list /etc/apt/sources.list.back && \
    cp /vulfocus-api/sources.list /etc/apt/sources.list && \
    apt update && \
    apt install nginx -y && \
    rm -rf /var/www/html/* && \
    cp /vulfocus-api/default /etc/nginx/sites-available/default && \
    cp /vulfocus-api/default /etc/nginx/sites-enabled/default && \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple some-package -r requirements.txt && \
    chmod u+x /vulfocus-api/run.sh
ADD dist/ /var/www/html/
CMD ["sh", "/vulfocus-api/run.sh"]