from django.conf.urls import url

from oauth.views import OAuthQQUserAPIView
from . import views

urlpatterns=[
    url(r'^qq/statues/$',views.OAuthQQURLAPIView.as_view()),
    url(r'^qq/users/$',OAuthQQUserAPIView.as_view())
]