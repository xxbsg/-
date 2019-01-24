from django.conf.urls import url

from .views import PlaceOrderAPIView, OrderAPIView

urlpatterns=[

    url(r'^places/$',PlaceOrderAPIView.as_view()),
    url(r'^$',OrderAPIView.as_view(),name='order'),
]