from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from meiduo_admin.views import users
from meiduo_admin.views.users import AdminLoginAPIView, AdminUserAPIView

urlpatterns = [
    url(r'^authorizations/$',AdminLoginAPIView.as_view()),
    # url(r'^authorizations/$',obtain_jwt_token)
    url(r'^users/$',AdminUserAPIView.as_view())


]