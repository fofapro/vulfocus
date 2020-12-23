from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from dockerapi.models import ContainerVul
import datetime
User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    # 利用drf中的validators验证username是否唯一
    username = serializers.CharField(required=True, allow_blank=False, validators=[UniqueValidator(queryset=User.objects.all(),message='用户已经存在')])
    password = serializers.CharField(
         style={"input_type": "password"},help_text="密码", label="密码", write_only=True,
     )

    def create(self, validated_data):
         user = super(UserRegisterSerializer, self).create(validated_data= validated_data)
         user.set_password(validated_data["password"])
         user.save()
         return user

    class Meta:
         model = User
         fields = ("username","password","email")


class UserProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_user_name')
    rank = serializers.SerializerMethodField('rankAD')
    rank_count = serializers.SerializerMethodField('rankCount')
    status_moudel = serializers.SerializerMethodField('set_status_moudel')
    roles = serializers.SerializerMethodField("set_role")

    class Meta:
        model = User
        fields = ("id", "name", "roles", "avatar", "email", "rank", "status_moudel", "rank_count")

    def get_user_name(self, obj):
        return obj.username

    def set_status_moudel(self, obj):
        return 0

    def rankAD(self, obj):
        rank = 0
        user_id = obj.id
        successful = ContainerVul.objects.filter(is_check=True, user_id=user_id, time_model_id="")
        for i in successful:
            rank += i.image_id.rank
        return rank

    def rankCount(self, obj):
        user_id = obj.id
        successful = ContainerVul.objects.filter(is_check=True, user_id=user_id, time_model_id="")
        return successful.count()

    def set_role(self, obj):
        if obj.is_superuser:
            return ["admin"]
        else:
            return ["member"]
