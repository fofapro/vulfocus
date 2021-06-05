from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import JsonResponse
from rest_framework import viewsets,mixins
from user.serializers import UserProfileSerializer, User, UserRegisterSerializer
from rest_framework.views import APIView
from django.contrib.auth import logout
from django.views.generic.base import View
from user.models import UserProfile
from dockerapi.common import R
from dockerapi.models import ContainerVul


class ListAndUpdateViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    A viewset that provides default `update()`, `list()`actions.
    """
    pass


class UserSet(ListAndUpdateViewSet):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return UserProfile.objects.all()
        else:
            return UserProfile.objects.all()

    def update(self, request, *args, **kwargs):
        user = request.user
        if not user.is_superuser:
            return JsonResponse(R.build(msg="权限不足"))
        print(self.get_object())
        new_pwd = request.data.get("pwd", "")
        new_pwd = new_pwd.strip()
        print(new_pwd)
        if len(new_pwd) < 6:
            return JsonResponse(R.build(msg="密码格式不正确"))
        user_info = self.get_object()
        user_info.set_password(new_pwd)
        user_info.save()
        return JsonResponse(R.ok())


class get_user_rank(APIView):

    def get(self, request):
        page_no = int(request.GET.get("page", 1))
        score_list = ContainerVul.objects.filter(is_check=True, time_model_id='').values('user_id').annotate(
            score=Sum("image_id__rank")).values('user_id', 'score').order_by("-score")
        try:
            pages = Paginator(score_list, 20)
            page = pages.page(page_no)
        except Exception as e:
            return JsonResponse(R.err())
        result = []
        for _data in list(page):
            user_info = UserProfile.objects.filter(id=_data["user_id"]).first()
            username = ""
            if user_info:
                username = user_info.username
            result.append({"rank": _data["score"], "name": username})
        data = {
            'results': result,
            'count': len(score_list)
        }
        return JsonResponse(R.ok(data=data))


class get_user_info(APIView):
    def get(self, request):
        user_info = User.objects.get(pk=request.user.id)
        serializer = UserProfileSerializer(user_info)
        return JsonResponse(serializer.data)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return JsonResponse({"msg": "OK"})


class UserRegView(viewsets.mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = []
    permission_classes = []
    queryset = UserProfile.objects.all()
    serializer_class = UserRegisterSerializer
