# coding:utf-8
from rest_framework import serializers
from layout_image.models import Layout, LayoutService, LayoutServiceNetwork, LayoutServiceContainer, LayoutData


class LayoutSerializer(serializers.ModelSerializer):

    class Meta:
        model = Layout
        fields = "__all__"


class LayoutServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = LayoutService
        fields = "__all__"


class LayoutServiceNetworkSerializer(serializers.ModelSerializer):

    class Meta:
        model = LayoutServiceNetwork
        fields = "__all__"


class LayoutServiceContainerSerializer(serializers.ModelSerializer):

    class Meta:
        model = LayoutServiceContainer
        fields = "__all__"


class LayoutDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = LayoutData
        fields = "__all__"

