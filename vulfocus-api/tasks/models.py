from django.db import models
import uuid

# Create your models here.


class TaskInfo(models.Model):
    """
    任务信息 Model
    """
    # task id
    task_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    # user id
    user_id = models.IntegerField(verbose_name="任务创建用户 ID")
    # task name
    task_name = models.CharField(max_length=255, verbose_name="任务名称", null=False)
    # task status, default 1, 1:start 2:execute 3:finish 4:except
    task_status = models.IntegerField(default=1, null=False)
    # task start date
    task_start_date = models.DateTimeField(auto_now_add=True, verbose_name="任务创建时间")
    # start end date
    task_end_date = models.DateTimeField(verbose_name="任务结束时间", null=True)
    # task operation 类型，1：拉取镜像 2：创建/启动 容器 3：停止容器 4：删除容器 5：分享镜像 6: build镜像 7: 创建docker compose
    operation_type = models.CharField(max_length=255, verbose_name="执行操作名称")
    # task operation args
    operation_args = models.TextField(verbose_name="执行操作参数", default="")
    # 任务执行消息
    task_msg = models.TextField(verbose_name="任务执行消息", default="")
    # 任务执行结果是否被查看
    is_show = models.BooleanField(default=False, verbose_name="任务是否被查看")
    # data create date
    create_date = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    # data update date
    update_date = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'task_info'
