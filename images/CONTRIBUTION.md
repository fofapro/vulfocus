## 贡献漏洞

### 更改镜像名称

将镜像名称更改为：vulshare/框架+cve编号:个人ID

例如：vulshare/weblogic-cve_2020_2883

docker tag 镜像名称 vulshare/xxx-cve_2020_xxx:r4v3zn

个人 ID 作为贡献来源

## 登录到hub.docker

使用命令：

1、登录 dockerhub：

`docker login --username vulshare`

接下来输入 token：

`2a295233-801b-4efb-9f78-916330b984f6`

出现Succeeded说明登录成功

### 上传到vulshare

`docker push vulshare/xxx-cve_2020_xxx:r4v3zn`

出现  sha256 说明上传成功

![](../imgs/6.png)

可直接到 https://hub.docker.com/u/vulshare , 进行查看。

![](../imgs/7.png)

