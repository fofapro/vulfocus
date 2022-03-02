# 安装(centos安装需要关闭selinux)

系统为前后端分离项目，`vulfocus-api`  为后端项目、 `vulfocus-frontend`  为前端项目。

## 快速安装

拉取 Vulfocus 镜像：
```
docker pull vulfocus/vulfocus:latest
```
运行 Vulfocus
```
docker create -p 80:80 -v /var/run/docker.sock:/var/run/docker.sock  -e VUL_IP=xxx.xxx.xxx.xxx -e EMAIL_HOST="xxx.xxx.xxx" -e EMAIL_HOST_USER="xxx@xxx.com" -e EMAIL_HOST_PASSWORD="xxxxxxxx" vulfocus/vulfocus
docker start container id
```
或者

```
docker run -d -p 80:80 -v /var/run/docker.sock:/var/run/docker.sock  -e VUL_IP=xxx.xxx.xxx.xxx -e EMAIL_HOST="xxx.xxx.xxx" -e EMAIL_HOST_USER="xxx@xxx.com" -e EMAIL_HOST_PASSWORD="xxxxxxxx" vulfocus/vulfocus
```
- `-v /var/run/docker.sock:/var/run/docker.sock` 为 docker 交互连接。
- `-e DOCKER_URL` 为 Docker 连接方式，默认通过 `unix://var/run/docker.sock` 进行连接，也可以通过 `tcp://xxx.xxx.xxx.xxx:2375` 进行连接（必须开放 2375 端口）。
- `-v /vulfocus-api/db.sqlite3:db.sqlite3` 映射数据库为本地文件。
- `-e VUL_IP=xxx.xxx.xxx.xxx` 为 **Docker** 服务器 IP ，不能为 127.0.0.1。
- `-e EMAIL_HOST="xxx.xxx.xxx"`  为邮箱SMTP服务器
- `-e EMAIL_HOST_USER="xxx@xxx.com"`  为邮箱账号
- `-e EMAIL_HOST_PASSWORD="xxxxxxxx`  为邮箱密码
- 默认账户密码为 `admin/admin`。

![](./imgs/login.png)

## 自定义安装(centos 7系统,需关闭selinux)

环境：

- 语言：python3
- 数据库：sqlite3、redis
- 框架：Django、Celery
- API：djangorestframework
- 系统：Centos 7 

### 安装依赖

#### 安装需要的软件和开发环境
```
yum -y install epel-release
yum install gcc -y
yum install  nginx supervisor net-tools wget git -y
yum install redis -y
```

### 安装 docker

#### 安装 docker

[https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)

```
yum install docker -y
```

#### Docker 配置

配置 Docker `2375` 端口（可根据实际情况进行修改），修改 docker 配置文件，加入以下信息：

**位置：**  `/usr/lib/systemd/system/docker.service`

```
ExecStart=/usr/bin/dockerd -H tcp://127.0.0.1:2375 -H unix://var/run/docker.sock \
```

或者

```
/usr/bin/dockerd-current -H tcp://127.0.0.1:2375 -H unix://var/run/docker.sock \
```

重载配置文件

```
systemctl daemon-reload
```



### 安装 Vulfocus API

#### 安装 Python3 

```shell
yum -y update
yum -y install yum-utils
sudo yum install https://repo.ius.io/ius-release-el7.rpm
sudo yum -y install python36u python36u-pip
```

#### 更新 pip

```shell
sudo pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
sudo pip3 install virtualenv -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 创建虚拟环境

```
mkdir -p /data/{etc,log,tmp}
chmod -R 777 /data
ln -s /usr/local/bin/virtualenv /usr/bin/virtualenv
virtualenv /data/venv_py --python=/usr/bin/python3
echo "source /data/venv_py/bin/activate" >> ~/.bashrc
source ~/.bashrc
```

#### 拉取 vulfocus 和安装项目依赖

```shell
cd /data
git clone https://github.com/fofapro/vulfocus.git web
chmod -R 777 /data
cd /data/web/vulfocus-api/
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
### 数据库配置

#### 如果使用mysql
```shell script
yum install mysql-devel 
pip3 install PyMysql -i https://pypi.tuna.tsinghua.edu.cn/simple
```
修改setting文件
```shell script
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vulfocus',
        'HOST':'127.0.0.1',
        'PORT':3306,
        'USER':'root',
        'PASSWORD':(此处填入你的mysql的root用户密码)
    }
}

#bug MySQL does not allow unique CharFields to have a max_length > 255
SILENCED_SYSTEM_CHECKS = ['mysql.E001']
```

### 注意
```sql
创建mysql数据库的时候应使用utf8编码，否则进行数据迁移的时候可能抛出错误,可以使用下面这条命令进行数据库的创建
CREATE DATABASE vulfocus character set utf8;
```

### 修改第三方库文件

```vim /data/venv_py/lib/python3.6/site-packages/django/db/backends/mysql/operations.py```

将该文件的145，146行用#注释掉

#### 初始化数据库

```shell
cd /data/web/vulfocus-api
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

#### 靶场配置：

2. 配置 VUL_IP（`vulfocus/settings.py`），修改为 Docker 服务器的 IP。

3. 修改 CELERY_BROKER_URL（`vulfocus/settings.py`），修改为 Redis 连接地址。

4. 配置 EMAIL_HOST;EMAIL_HOST_USER;EMAIL_HOST_PASSWORD,修改为自己的邮箱配置

#### 安装uwsgi

```shell
yum install python36u-devel
pip install uwsgi -i https://pypi.tuna.tsinghua.edu.cn/simple
```

##### uwsgi 配置

**位置：** `/data/etc/vulfocus_uwsgi.ini`

```shell
[uwsgi]
uid=nginx
chdir = /data/web/vulfocus-api
module = vulfocus.wsgi
mount = /api=vulfocus.wsgi:application
manage-script-name = true
home = /data/venv_py
socket = /data/tmp/vulfocus_uwsgi.sock
processes = 8
master = true
max-requests = 6000
chmod-socket = 777
vacuum = true
enable-threads = true
single-interpreter = true
```

#### nginx配置

**位置：**`/etc/nginx/nginx.conf`

```
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 2048;
    client_max_body_size 4096M;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    include /etc/nginx/conf.d/*.conf;

    server {
        listen       80 default_server;
        listen       [::]:80 default_server;
        server_name  _;

        # Load configuration files for the default server block.
        include /etc/nginx/default.d/*.conf;

       location /{
           root /data/web/dist;
       index index.html;
       }
       location /images/ {
                alias /data/web/vulfocus-api/static/;
       }
       location /api {
              uwsgi_pass  unix:/data/tmp/vulfocus_uwsgi.sock;
              uwsgi_read_timeout 600;
              uwsgi_param SCRIPT_NAME /api;
              include     /etc/nginx/uwsgi_params;
}
    access_log  /data/log/vulfocus.access.log;
    error_log  /data/log/vulfocus.error.log;

    }


}
```

### 配置supervisor

**位置：**`/etc/supervisord.d/vulfocus.ini`

```
[program:vulfocus]
directory=/data/venv_py
command=/data/venv_py/bin/uwsgi --ini /data/etc/vulfocus_uwsgi.ini
numprocs=1
user=nginx
startretries=3
startsecs=5
autostart=true
autorestart=true
stopsignal=INT
stopasgroup=true
killasgroup=true
redirect_stderr=true
stdout_logfile=/data/log/vulfoucs_uwsgi.log
```
### 权限以及自启

```
chown -R nginx /data
```

将nginx用户加入docker用户组

```
groupadd docker
usermod -g docker nginx
```

#### 开机自启动

```
systemctl enable nginx
systemctl enable supervisord
systemctl enable docker
systemctl enable redis
```

#### 启动服务

```
systemctl start supervisord
systemctl start docker
systemctl start redis
systemctl start nginx    #注意这里一定要确定主机关闭了selinux，否则启动nginx会报错
chmod 666 /var/run/docker.sock #注意此处完成配置后尽量不要重新启动docker,否则nginx用户将失去docker的运行权限
```

#### 启动 Celery后台任务

在/data/web/vulfocus-api目录下执行如下命令

```
celery multi start worker -B -A  vulfocus -l info --logfile=celery.log
```



#### 防火墙配置

```shell script
firewall-cmd --add-port=80/tcp --permanent
firewall-cmd --add-port=443/tcp --permanent
systemctl restart firewalld.service
```

### 问题

拉取镜像会报 500 错误这个是 `/var/run/docker.sock` 权限问题

三种解决方案

1. 修改 `/etc/supervisord.d/vulfocus.ini` 配置文件

   ```
   # user=nginx # 改前
   user=root # 改后
   ```

2. 配置 Docker URL（`vulfocus/settings.py`），启用 `tcp://127.0.0.1:2375`

3. 添加 docker 用户组把 nginx 用户加进去

   ```
   groupadd docker
   usermod -aG docker nginx
   chmod 666 /var/run/docker.sock #注意此处完成配置后尽量不要重新启动docker,否则nginx用户将失去docker的运行权限
   ```



## docker-compose 安装

#### 拉取 vulfocus 和安装项目依赖

```
cd /data
git clone https://github.com/fofapro/vulfocus.git web
```

#### 配置环境参数

```
cd /data/web
vim docker-compose.yaml
```
#### 修改环境运行ip

将环境变量VUL_IP替换成本机ip

![](https://img.wenhairu.com/images/2022/02/26/ROK6U.png)



#### 启动项目

```
docker-compose up
```

这时浏览器地址栏输入本机ip即可访问vulfocus服务

