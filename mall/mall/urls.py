"""mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin



urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^users/',include('users.urls',namespace='users')),
    url(r'^verifications/',include('verifications.urls',namespace='verifications')),
    url(r'^oauth/', include('oauth.urls', namespace='oauth')),
    url(r'^areas/', include('areas.urls', namespace='araes')),
    # 富文本
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),

    url(r'^goods/', include('goods.urls', namespace='goods')),
    # 购物车
    url(r'^cart/',include('carts.urls',namespace='carts')),

    # 订单结算
    url(r'^orders/',include('orders.urls',namespace='orders')),

    # 支付
    url(r'^pay/',include('pay.urls',namespace='pay')),
]
