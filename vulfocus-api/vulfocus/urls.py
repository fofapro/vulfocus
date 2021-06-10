"""vulbox URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from rest_framework import routers
from dockerapi.views import ImageInfoViewSet, ContainerVulViewSet, SysLogSet, get_setting, update_setting, TimeMoudelSet, CreateTimeTemplate, UserRank, TimeRankSet, get_timing_imgs
from user.views import UserRegView, UserSet, get_user_rank
from rest_framework_jwt.views import obtain_jwt_token
from user.views import get_user_info, LogoutView
from tasks.views import TaskSet
from network.views import NetWorkInfoViewSet
from layout_image.views import LayoutViewSet, upload_img

router = routers.DefaultRouter()
router.register('images', ImageInfoViewSet, basename='Images')
router.register('container', ContainerVulViewSet, basename='Container')
router.register('user/register', UserRegView, basename='register')
router.register('user', UserSet, basename='user')
router.register('syslog', SysLogSet, basename="SysLog")
router.register('tasks', TaskSet, basename="TaskSet")
router.register("network", NetWorkInfoViewSet, basename="network")
router.register('layout', LayoutViewSet, basename="layout")
router.register('time', TimeMoudelSet, basename="time")
router.register('timetemp', CreateTimeTemplate, basename="timetmep")
router.register('userrank', UserRank, basename="user_rank")
router.register('timerank', TimeRankSet, basename="time_rankset")

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^user/login', obtain_jwt_token),
    url(r'^user/logout', LogoutView.as_view(), name="logout"),
    url(r'^user/info', get_user_info.as_view()),
    url(r'^rank/user', get_user_rank.as_view()),
    url(r'setting/get', get_setting),
    url(r'setting/update', update_setting),
    url(r'img/upload', upload_img),
    url(r'get/website/imgs', get_timing_imgs),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
