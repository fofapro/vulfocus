from django.db import models
import uuid
from user.models import UserProfile
# Create your models here.


class TimeTemp(models.Model):
    """
    时间模式模板信息
    """
    temp_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=256, verbose_name="模版名称", default="")
    user_id = models.IntegerField(verbose_name='用户ID')
    time_range = models.IntegerField(verbose_name='计时模式时间')
    image_name = models.TextField(null=False, default="", verbose_name="图片名称")
    time_desc = models.TextField(verbose_name='计时模版描述', null=True)
    time_img_type = models.TextField(verbose_name="漏洞类型", default="")
    rank_range = models.TextField(verbose_name="Rank范围", default="")
    flag_status = models.BooleanField(verbose_name='用于判断', default=False)
    image_ids = models.TextField(verbose_name="镜像id", default="")
    # 1是盲盒模式 2是普通模式
    template_pattern = models.IntegerField(verbose_name="计时模式分类", default=1)
    total_view = models.IntegerField(default=0, verbose_name="查看数")

    class Meta:
        db_table = 'time_temp'


class TimeRank(models.Model):
    """
    时间模式排名
    """
    rank_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user_id = models.IntegerField(verbose_name='用户ID')
    user_name = models.CharField(max_length=256, verbose_name='用户名称')
    rank = models.FloatField(verbose_name='Rank', null=False)
    time_temp = models.ForeignKey(to="TimeTemp", to_field='temp_id', on_delete=models.CASCADE)

    class Meta:
        db_table = 'time_rank'


class TimeMoudel(models.Model):
    """
    时间模式信息
    """
    time_id = models.CharField(max_length=255, default=str(uuid.uuid4()), primary_key=True,verbose_name='ID')  # 关键
    user_id = models.IntegerField(verbose_name='用户ID')
    start_time = models.FloatField(null=False, verbose_name='开始时间戳')  # 时间模式开始时间
    end_time = models.FloatField(null=False, verbose_name='结束时间')  # 时间模式结束时间
    temp_time_id = models.ForeignKey(to="TimeTemp", to_field='temp_id', on_delete=models.CASCADE)  # 关联模版id
    status = models.BooleanField(verbose_name='用于判断', default=False)

    class Meta:
        db_table = 'time_moudel'


class ImageInfo(models.Model):
    """
    镜像实体Model
    """
    image_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    image_name = models.CharField(max_length=256, unique=True, verbose_name='Docker镜像名称', null=False)
    image_vul_name = models.CharField(max_length=256, verbose_name='漏洞名称', null=False)
    image_port = models.CharField(null=True, default="", verbose_name='暴露端口', max_length=256)
    image_desc = models.TextField(verbose_name='镜像描述', null=True)
    rank = models.FloatField(verbose_name='Rank', null=False)
    is_ok = models.BooleanField(verbose_name="镜像是否可用", default=True)
    is_share = models.BooleanField(verbose_name="镜像是否贡献", default=False)
    degree = models.TextField(verbose_name="漏洞类型", default="", blank=True)
    writeup_date = models.TextField(verbose_name="writeup", default="")
    is_flag = models.BooleanField(verbose_name="是否展示flag输入框", default=True)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Docker创建时间，默认为当前时间')
    update_date = models.DateTimeField(auto_now_add=True, verbose_name='Docker更新时间，默认为当前时间')
    is_docker_compose = models.BooleanField(verbose_name="镜像启动方式", default=False)
    docker_compose_yml = models.TextField(verbose_name="compose_yml", default="")
    docker_compose_env = models.TextField(verbose_name="env_port", default="")
    compose_env_port = models.TextField(verbose_name="env对应端口", default="")
    original_yml = models.TextField(verbose_name="原生yml文件", default="")
    class Meta:
        db_table = 'image_info'


class ContainerVul(models.Model):
    """
    容器实体Model
    """
    container_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, verbose_name='漏洞容器创建ID')
    docker_container_id = models.CharField(max_length=255, verbose_name='Docker容器运行进ID')
    image_id = models.ForeignKey(ImageInfo, on_delete=models.CASCADE, verbose_name='镜像ID')
    user_id = models.IntegerField(verbose_name='用户ID')
    vul_host = models.CharField(max_length=255, verbose_name='容器漏洞URL')
    container_status = models.CharField(max_length=255, verbose_name='容器当前状态')
    container_port = models.CharField(max_length=255, verbose_name='容器端口')
    vul_port = models.TextField(verbose_name="容器对应端口", default="")
    container_flag = models.CharField(max_length=255, verbose_name='flag')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='容器创建时间，默认为当前时间')
    is_check = models.BooleanField(default=False, verbose_name='Flag是否通过')
    is_check_date = models.DateTimeField(null=True, verbose_name='Flag提交时间')
    time_model_id = models.CharField(max_length=255, verbose_name='时间模式 ID')
    docker_compose_path = models.TextField(verbose_name="docker_compose_path", default="")  # docker-compose 相关运行路径
    is_docker_compose_correlation = models.BooleanField(verbose_name="docker-compose相关辅助镜像", default=False)

    class Meta:
        db_table = 'container_vul'


class SysLog(models.Model):
    # id
    log_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, verbose_name="ID")
    # 操作人员ID
    user_id = models.IntegerField(verbose_name="使用用户ID")
    # 操作类型字段
    operation_type = models.CharField(max_length=255, verbose_name="操作类型")
    # 操作名称
    operation_name = models.CharField(max_length=255, verbose_name="操作名称")
    # 操作内容
    operation_value = models.CharField(max_length=255, verbose_name="操作内容")
    # 操作参数
    operation_args = models.TextField(verbose_name='参数', null=True, default="")
    # ip
    ip = models.CharField(max_length=255, verbose_name="IP地址")
    # 创建时间
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = "sys_log"


class SysConfig(models.Model):
    """
    数据库字段内容禁止删除
    """
    config_key = models.CharField(max_length=255, verbose_name="配置名称对应key", unique=True)
    config_value = models.TextField(verbose_name="对应值", null=True, default="")

    class Meta:
        db_table = "sys_config"
