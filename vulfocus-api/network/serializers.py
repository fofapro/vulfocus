from rest_framework import serializers
from network.models import NetWorkInfo


class NetWorkInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetWorkInfo
        fields = '__all__'
