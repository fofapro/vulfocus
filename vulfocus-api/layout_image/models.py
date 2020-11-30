from django.db import models
import uuid
# Create your models here.


class LayoutImage(models.Model):
    layout_id = models.UUIDField(default=uuid.uuid4(), editable=False, primary_key=True, verbose_name="编排UUID")
    layout_name = models.CharField(max_length=255, null=False, verbose_name="环境名称")
    yml_content = models.TextField(null=False, verbose_name="编排内容")
    env_content = models.TextField(null=False, verbose_name="环境变量")
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_date = models.DateTimeField(auto_now=True, verbose_name='更新时间')
