from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from dockerapi.models import ContainerVul,ImageInfo
from dockerapi.serializers import ImageInfoSerializer
from user.models import UserProfile, RegisterCode
import datetime
User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    # 利用drf中的validators验证username是否唯一
    username = serializers.CharField(required=True, allow_blank=False, max_length=20,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message='用户已经存在')],
                                     error_messages={"blank": "用户名不能为空", "required": "用户名不能为空",
                                                     "max_length": "用户名不能超过20位"})
    password = serializers.CharField(
         style={"input_type": "password"}, help_text="密码", label="密码", write_only=True, error_messages={"blank": "密码不能为空", "required": "密码不能为空"})
    checkpass = serializers.CharField(style={"input_type_password"}, allow_blank=False, write_only=True)
    code = serializers.CharField(required=True, allow_blank=False, write_only=True)
    def create(self, validated_data):
        username = validated_data["username"]
        password = validated_data["password"]
        code = validated_data["code"]
        register_code = RegisterCode.objects.filter(code=code).first()
        user = UserProfile(username=username, email=register_code.email)
        user.set_password(password)
        user.save()
        register_code.delete()
        return user

    class Meta:
         model = User
         fields = ("username", "password", "checkpass", "code")


class UserProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_user_name')
    rank = serializers.SerializerMethodField('rankAD')
    rank_count = serializers.SerializerMethodField('rankCount')
    status_moudel = serializers.SerializerMethodField('set_status_moudel')
    roles = serializers.SerializerMethodField("set_role")
    date_joined = serializers.SerializerMethodField("transition_time")

    class Meta:
        model = User
        fields = ("id", "name", "roles", "avatar", "email", "rank", "status_moudel", "rank_count", "date_joined", 'greenhand')

    def transition_time(self,obj):
        time = obj.date_joined.strftime('%Y-%m-%d %H:%M:%S')
        return time

    def get_user_name(self, obj):
        return obj.username

    def set_status_moudel(self, obj):
        return 0

    def rankAD(self, obj):
        rank = 0
        user_id = obj.id
        successful = ContainerVul.objects.filter(is_check=True, user_id=user_id, time_model_id="").values('image_id').distinct()
        if successful:
            img = ImageInfo.objects.filter(image_id=i['image_id']).first()
            rank += img.rank
        return rank

    def rankCount(self, obj):
        user_id = obj.id
        successful = ContainerVul.objects.filter(is_check=True, user_id=user_id, time_model_id="").values('image_id').distinct()
        return successful.count()

    def set_role(self, obj):
        if obj.is_superuser:
            return ["admin"]
        else:
            return ["member"]

#修改密码
class UpdatePassSerializer(serializers.ModelSerializer):
    new_password=serializers.CharField(style={"input_type":"password"},min_length=6,help_text="新密码",label="新密码",write_only=True)

    class Meta:
        model=User
        fields=["new_password"]


class LoginSerializer(serializers.ModelSerializer):
    username=serializers.CharField(help_text="用户名",label="用户名",allow_blank=False,required=True,allow_null=False,write_only=True)
    password=serializers.CharField(help_text="密码",label="密码",allow_blank=False,required=True,style={"input_type":"password"},allow_null=False,write_only=True)
    # code=serializers.CharField(help_text="验证码",label="验证码",allow_blank=False,required=True,allow_null=False,write_only=True)

    class Meta:
        model=User
        fields=["username","password"]



class SendEmailSerializer(serializers.Serializer):
    username=serializers.CharField(help_text="用户名",label="用户名",required=True)


#重置密码
class ResetPasswordSerializer(serializers.ModelSerializer):
    code=serializers.CharField(min_length=4,required=True,help_text="验证码",label="验证码",write_only=True)
    password=serializers.CharField(style={"input_type":"password"},help_text="新密码",label="新密码",required=True)

    class Meta:
        model=User
        fields=["code","password"]