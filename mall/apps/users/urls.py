from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from . import views
from .views import RegisterUsernameCountAPIView, UserCenterInfoAPIView, UserEmailInfoAPIView,UserEmailVerificationAPIView, \
    AddressViewSet

urlpatterns = [
    url(r'^usernames/(?P<username>\w{5,20})/count/$',views.RegisterUsernameCountAPIView.as_view(),name='usernamecount'),
    # url(r'^usernames/(?P<username>\w{5,20})/count/$',views.RegisterUsernameAPIView.as_view(),name='usernamecount'),

    # url(r'^phones/(?P<mobile>1[345789]\d{9})/count/$',views.RegisterPhoneCountAPIView.as_view(),name='phonecount'),
    url(r'^phones/(?P<mobile>1[345789]\d{9})/count/$',views.RegisterPhoneCountAPIView.as_view(), name='phonecount'),

    url(r'^$',views.RegisterUserAPIView.as_view()),

    # 实现登录
    # url(r'^auths/',obtain_jwt_token),
    url(r'^auths/',views.MergeLoginAPIView.as_view()),
    # 个人中心展示
    url(r'^infos/$',UserCenterInfoAPIView.as_view()),
    # 邮箱
    url(r'^emails/$',UserEmailInfoAPIView.as_view()),
    url(r'^emails/verification/$',UserEmailVerificationAPIView.as_view()),

    # url(r'^addresses/$',AddressViewSet.as_view()),

    url(r'^browerhistories/$', views.UserHistoryAPIView.as_view(), name='history'),
    url(r'^(?P<user_id>\d+)/password/$', views.UserUpdatePasswordAPIView.as_view()),
    url(r'^(?P<user_id>\d+)/passwords/$', views.UserResetPasswordAPIView.as_view())

]
from .views import AddressViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'addresses',AddressViewSet,base_name='address')
urlpatterns += router.urls
