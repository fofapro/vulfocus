from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    avatar = models.CharField(max_length=100, null=True, blank=True, verbose_name="头像",default="http://www.baimaohui.net/home/image/icon-anquan-logo.png")
    role = models.CharField(max_length=10, default="注册用户", verbose_name="角色")

    def __str__(self):
        return self.username
