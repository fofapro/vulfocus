from django.db import models
import uuid

# Create your models here.
# 系统通知模块


class Notice(models.Model):
    notice_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    title = models.CharField(max_length=255, verbose_name="公告名称", null=False)
    notice_content = models.TextField(verbose_name="公告内容", null=False)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_date = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_newest = models.BooleanField(verbose_name="是否最新发布", default=False)
    is_public = models.BooleanField(verbose_name="是否已经发布", default=False)

    class Meta:
        db_table = "notice_info"
