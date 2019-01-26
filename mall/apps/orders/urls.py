from django.conf.urls import url

from .views import PlaceOrderAPIView, OrderAPIView, shangpin,shangpinpl

urlpatterns=[

    url(r'^places/$',PlaceOrderAPIView.as_view()),
    url(r'^$',OrderAPIView.as_view(),name='order'),
    # url(r'^$',OrderListAPIView.as_view()),
    #http://api.meiduo.site:8000/orders/20190125131013000008/uncommentgoods/
    url(r'(?P<odid>\d+)/uncommentgoods/',shangpin.as_view()),
    #http: // api.meiduo.site: 8000 / orders / 20190125124038000008 / comments /
    url(r'(?P<odid>\d+)/comments/',shangpinpl.as_view()),

]