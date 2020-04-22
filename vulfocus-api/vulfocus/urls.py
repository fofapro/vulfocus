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
# from django.contrib import admin
from django.conf.urls import url, include
from rest_framework import routers
from dockerapi.views import ImageInfoViewSet, ContainerVulViewSet, SysLogSet
from user.views import UserRegView, UserSet
from rest_framework_jwt.views import obtain_jwt_token
from user.views import get_user_info, LogoutView

router = routers.DefaultRouter()
router.register('images', ImageInfoViewSet, base_name='Images')
router.register('container', ContainerVulViewSet, base_name='Container')
router.register('user/register', UserRegView, base_name='register')
router.register('user', UserSet, base_name='user')
router.register('syslog', SysLogSet, base_name="SysLog")
# check_docker_status

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^user/login', obtain_jwt_token),
    url(r'^user/logout', LogoutView.as_view(), name="logout"),
    url(r'user/info', get_user_info.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #    path('admin/', admin.site.urls),
]
