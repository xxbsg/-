from django.conf.urls import url

from carts.views import CartAPIView

urlpatterns=[
    url(r'^$',CartAPIView.as_view())
]