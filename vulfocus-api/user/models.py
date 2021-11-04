from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class UserProfile(AbstractUser):
    avatar = models.CharField(max_length=100, null=True, blank=True, verbose_name="头像", default="/images/user/bmh.png")
    role = models.CharField(max_length=10, default="注册用户", verbose_name="角色")
    greenhand = models.BooleanField(verbose_name='用户是否首次登录', default=False)
    has_active = models.BooleanField(verbose_name="用户是否激活", default=True)
    licence = models.CharField(max_length=191, default=str(uuid.uuid1()).replace("-", ""))
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


class Comment(models.Model):
    comment_id = models.UUIDField(default=uuid.uuid4(), editable=False, primary_key=True, verbose_name="评论UUID")
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="用户")
    scene_id = models.CharField(max_length=255, verbose_name="关联场景id")
    # 计时场景，编排场景， 盲盒模式等。。。
    scene_type = models.CharField(max_length=255, verbose_name="场景类型")
    content = models.TextField(null=True, verbose_name="评论内容")
    create_time = models.DateTimeField(null=True, auto_now_add=True, verbose_name='评论时间，默认为当前时间')

    class Meta:
        db_table = "comment"
