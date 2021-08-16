from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    avatar = models.CharField(max_length=100, null=True, blank=True, verbose_name="头像", default="http://www.baimaohui.net/home/image/icon-anquan-logo.png")
    role = models.CharField(max_length=10, default="注册用户", verbose_name="角色")
    greenhand = models.BooleanField(verbose_name='用户是否首次登录', default=False)
    def __str__(self):
        return self.username

#邮箱验证码
class EmailCode(models.Model):
    email=models.EmailField(null=False,blank=False,verbose_name="用户邮箱")
    code=models.CharField(max_length=20,verbose_name="验证码")
    user=models.ForeignKey(UserProfile,on_delete=models.CASCADE,verbose_name="用户")
    add_time=models.DateTimeField(auto_now_add=True,verbose_name="添加时间")


    class Meta:
        verbose_name="验证码"
        verbose_name_plural=verbose_name

class RegisterCode(models.Model):
    email = models.EmailField(null=False, blank=False, verbose_name="用户邮箱")
    code = models.CharField(max_length=20, verbose_name="验证码")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
