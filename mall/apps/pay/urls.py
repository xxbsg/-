from django.conf.urls import url
from . import views

urlpatterns = [
    #/pay/orders/(?P<order_id>)\d+/
    url(r'^orders/(?P<order_id>\d+)/$',views.PaymentAPIView.as_view(),name='pay'),
    #http://api.meiduo.site:8000/pay/status/
    url(r'^status/$',views.Ddwc.as_view())
]