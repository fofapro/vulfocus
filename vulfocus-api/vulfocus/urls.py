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
from dockerapi.views import ImageInfoViewSet, ContainerVulViewSet, SysLogSet, get_setting, update_setting, TimeMoudelSet, CreateTimeTemplate, UserRank, TimeRankSet, get_timing_imgs, DashboardView, get_writeup_info, get_version, get_url_name, update_enterprise_setting, get_setting_img
from user.views import UserRegView, UserSet, get_user_rank, LoginViewset, SendEmailViewset, ResetPasswordViewset, UpdatePassViewset, AccessLinkView, send_register_email
from rest_framework_jwt.views import obtain_jwt_token
from user.views import get_user_info, LogoutView, MyCode, refresh_captcha, CommentView
from tasks.views import TaskSet
from network.views import NetWorkInfoViewSet
from layout_image.views import LayoutViewSet, upload_img, build_compose, show_compose, upload_file, delete_file, update_build_compose, get_scene_data, upload_zip_file, download_layout_image, download_official_website_layout,get_official_website_layout
from user.views import refresh_captcha, AccessUpdataLinkView, upload_user_img
from notice.views import NoticeViewset, publish_notice, get_notifications_count, get_public_notice, notice_detail, get_content
from dockerapi.views import get_container_status
import notifications.urls
from layout_image.views import thumbUp

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
router.register("changepassword",UpdatePassViewset,basename="changepassword")
#自定义登录
router.register("login",LoginViewset,basename="login")
router.register("send_email",SendEmailViewset,basename="send_email")
router.register("reset_password",ResetPasswordViewset,basename="reset_password")
router.register("notice", NoticeViewset, basename="notice")
router.register("comment", CommentView, basename="comment")

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^user/login', obtain_jwt_token),
    url(r'^user/logout', LogoutView.as_view(), name="logout"),
    url(r'^img/dashboard', DashboardView.as_view()),
    url(r'^user/info', get_user_info.as_view()),
    url(r'^rank/user', get_user_rank.as_view()),
    url(r'setting/get', get_setting),
    url(r'setting/update', update_setting),
    url(r'enterprise/update', update_enterprise_setting),
    url(r'img/upload', upload_img),
    url(r'get/urlname', get_url_name),
    url(r'get/scenedata', get_scene_data),
    url(r'get/website/imgs', get_timing_imgs),
    url(r'^get/settingimg', get_setting_img),
    url(r'^getcaptcha/', MyCode.as_view()),
    url(r'^build/compose/', build_compose),
    url(r'^update/compose/', update_build_compose),
    url(r'^show/compose/', show_compose),
    url(r'^file/upload/', upload_file),
    url(r'^file/delete/', delete_file),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r"accesslink",AccessLinkView.as_view()),
    url(r'send_register_email', send_register_email),
    url(r'captcha/', include("captcha.urls")),
    url(r'refresh_captcha/', refresh_captcha),
    url(r"accessupdatelink",AccessUpdataLinkView.as_view()),
    url(r'uploaduserimg',upload_user_img),
    url(r'get_writeup', get_writeup_info),
    url(r'timerank', TimeRankSet.as_view()),
    url(r'get_version', get_version),
    url(r'inbox/notifications', include((notifications.urls, notifications))),
    url(r'public_notice', publish_notice),
    url(r"get_notices", get_public_notice),
    url(r"notice_detail", notice_detail),
    url(r'get_notifications_count',get_notifications_count),
    url(r"get_content", get_content),
    url(r"get_container_status",get_container_status),
    url(r"upload_zip_file", upload_zip_file),
    url(r"download_layout_image", download_layout_image),
    url(r"^download/official/website/layout", download_official_website_layout),
    url(r"^get/official/website/layout", get_official_website_layout),
    url(r"thumbUp", thumbUp),
]
