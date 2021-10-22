from django.db import models
import uuid
from dockerapi.models import ImageInfo
from network.models import NetWorkInfo
from user.models import UserProfile

class Layout(models.Model):
    """
    编排环境名称
    """
    layout_id = models.UUIDField(default=uuid.uuid4(), editable=False, primary_key=True, verbose_name="编排UUID")
    layout_name = models.CharField(max_length=255, null=False, verbose_name="环境名称")
    layout_desc = models.TextField(null=True, verbose_name="描述")
    image_name = models.TextField(null=False, default="", verbose_name="图片名称")
    create_user_id = models.IntegerField(verbose_name='用户ID')
    is_release = models.BooleanField(null=False, default=False, verbose_name="是否发布，默认否")
    raw_content = models.TextField(null=False, default="", verbose_name="原json内容")
    yml_content = models.TextField(null=False, verbose_name="编排内容")
    env_content = models.TextField(null=False, verbose_name="环境变量")
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_date = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_uesful = models.BooleanField(default=True, verbose_name="编排环境是否可用")
    total_view = models.IntegerField(default=0, verbose_name="查看数")
    download_num = models.IntegerField(default=0, verbose_name="下载数")

    class Meta:
        db_table = "layout"


class LayoutService(models.Model):
    """
    编排环境镜像关系表，服务层
    """
    service_id = models.UUIDField(default=uuid.uuid4(), editable=False, primary_key=True, verbose_name="ID")
    layout_id = models.ForeignKey(Layout, on_delete=models.CASCADE, verbose_name="编排 ID")
    image_id = models.ForeignKey(ImageInfo, on_delete=models.CASCADE, verbose_name='镜像ID')
    service_name = models.TextField(null=False, default="", verbose_name="服务环境名称")
    is_exposed = models.BooleanField(editable=False, verbose_name="是否暴露")
    exposed_source_port = models.CharField(max_length=255, null=False, verbose_name="暴露原端口")
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_date = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = "layout_service"


class LayoutServiceNetwork(models.Model):
    """
    编排环境镜像相关网卡表
    """
    layout_service_network_id = models.UUIDField(default=uuid.uuid4(), editable=False, primary_key=True, verbose_name="ID")
    service_id = models.ForeignKey(LayoutService, on_delete=models.CASCADE, verbose_name="服务ID")
    network_id = models.ForeignKey(NetWorkInfo, on_delete=models.CASCADE, verbose_name="网卡名称")
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_date = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = "layout_service_network"


class LayoutData(models.Model):
    """
    编排环境用户运行信息表
    """
    layout_user_id = models.UUIDField(default=uuid.uuid4(), editable=False, primary_key=True, verbose_name="ID")
    create_user_id = models.IntegerField(verbose_name='用户ID')
    layout_id = models.ForeignKey(Layout, on_delete=models.CASCADE, verbose_name="编排 ID")
    status = models.CharField(max_length=255, null=False, verbose_name="状态信息")
    file_path = models.TextField(null=False, default="", verbose_name="启动目录")
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_date = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = "layout_data"


class LayoutServiceContainer(models.Model):
    """
    服务运行容器表
    """
    # id
    service_container_id = models.UUIDField(default=uuid.uuid4(), editable=False, primary_key=True, verbose_name="ID")
    # user id
    user_id = models.IntegerField(verbose_name='用户ID')
    # docker id
    docker_container_id = models.CharField(max_length=255, verbose_name='Docker容器运行ID')
    # 编排环境用户运行信息表
    layout_user_id = models.ForeignKey(LayoutData,  on_delete=models.CASCADE, verbose_name="编排环境运行信息")
    # 服务 id
    service_id = models.ForeignKey(LayoutService, on_delete=models.CASCADE, verbose_name="服务ID")
    # 镜像 id
    image_id = models.ForeignKey(ImageInfo, on_delete=models.CASCADE, verbose_name="镜像ID")
    # 容器 host
    container_host = models.CharField(max_length=255, verbose_name='容器漏洞URL')
    # 容器状态 running stop
    container_status = models.CharField(max_length=255, verbose_name='容器当前状态')
    # 容器暴露端口
    container_port = models.CharField(max_length=255, verbose_name='容器端口')
    # flag
    container_flag = models.CharField(max_length=255, verbose_name='flag')
    # 创建时间
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='容器创建时间，默认为当前时间')
    # 更新时间
    update_date = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = "layout_service_container"


class LayoutServiceContainerScore(models.Model):
    # id
    layout_service_container_score_id = models.UUIDField(default=uuid.uuid4(), editable=False, primary_key=True, verbose_name="ID")
    # flag 提交用户 ID
    user_id = models.IntegerField(verbose_name='用户ID')
    # 环境 ID
    layout_id = models.ForeignKey(Layout, on_delete=models.CASCADE, verbose_name="编排 ID")
    # 环境 ID
    layout_data_id = models.ForeignKey(LayoutData, on_delete=models.CASCADE, verbose_name="编排 ID")
    # 服务编排id
    service_container_id = models.ForeignKey(LayoutServiceContainer, on_delete=models.CASCADE, verbose_name="编排 ID")
    # 服务 id
    service_id = models.ForeignKey(LayoutService, on_delete=models.CASCADE, default=None, verbose_name="服务ID")
    # 镜像 id
    image_id = models.ForeignKey(ImageInfo, on_delete=models.CASCADE, default=None, verbose_name="镜像ID")
    # 用户提交flag
    flag = models.CharField(max_length=255, null=False, verbose_name="flag")
    # 创建时间
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间，默认为当前时间')
    # 更新时间
    update_date = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = "layout_service_container_score"


class SceneUserFav(models.Model):
    """
    场景点赞模型
    """
    scene_id = models.CharField(max_length=255, verbose_name="场景id")
    user = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, verbose_name="点赞用户")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        db_table = "layout_user_fav"
