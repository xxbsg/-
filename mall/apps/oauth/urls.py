from django.conf.urls import url

from oauth.views import OAuthQQUserAPIView
from . import views

urlpatterns=[
    url(r'^qq/statues/$',views.OAuthQQURLAPIView.as_view()),
    url(r'^qq/users/$',OAuthQQUserAPIView.as_view()),
    url(r'^weibo/statues/$', views.OAuthSinaUrlAPIView.as_view()),
    #http://api.meiduo.site:8000/oauth/sina/user/?code=4168dfe1ce77b1bae1781dbcc0ddfae1
    url(r'^sina/user/$',views.OAuthSinaUserAPIView.as_view())
]