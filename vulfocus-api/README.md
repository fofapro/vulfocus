# vulfocus API

环境：

- 语言：python3
- 数据库：sqlite3、redis
- 框架：Django、Celery
- API：djangorestframework
- 系统：Centos 7 , Other

安装 Docker:

[https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)

安装 Redis：

[https://www.runoob.com/redis/redis-install.html](https://www.runoob.com/redis/redis-install.html)

安装依赖：

```
pip install -r requirements.txt
```

创建数据库：

```
python manage.py migrate
```

创建管理员用户：

```
python manage.py createsuperuser
```

靶场配置：

1. 配置 Docker URL（`vulfocus/settings.py`），默认为：`tcp://127.0.0.1:2375`，修改为 Docker 服务器的 IP。

2. 配置 VUL_IP（`vulfocus/settings.py`），修改为 Docker 服务器的 IP。

启动 API 后端：

```
python manage.py runserver 0.0.0.0:8000
```

启动 Celery：

```
celery multi start worker -A vulfocus -l info --logfile=celery.log
```

### 部署

####  Docker 配置

配置 Docker 2375 端口（可根据实际情况进行修改），修改 docker 配置文件，加入以下信息：

```
ExecStart=/usr/bin/dockerd -H tcp://127.0.0.1:2375 -H unix://var/run/docker.sock \
```

配置上传文件大小，修改 `nginx.conf` 文件，http 中加入：

```
client_max_body_size 4096M;
```

其中 4096M（4GB） 为上传文件最大限制，可根据实际进行修改，最小配置为 200M 。

#### Linux 部署

修改 nginx 配置目录 `sites-enabled` 中 `default` 文件 ，server 节点添加以下代码：

```
location /api/ {
		proxy_pass http://127.0.0.1:8000/;
}
```

#### Windows 部署

修改 nginx 配置文件 `nginx.conf` ，server 添加以下代码：

```
location /api/ {
		proxy_pass http://127.0.0.1:8000/;
}
```

#### nginx 参考配置文件

以下为 nginx 参考配置文件：

```
worker_processes  1;
events {
    worker_connections  1024;
}
http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;
    client_max_body_size 4096M;
    server {
        listen       80;
        server_name  localhost;
        location / {
            root   html;
            index  index.html index.htm;
        }
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }
        location /api/ {
                proxy_pass http://127.0.0.1:8000/;
        }
    }
}
```

