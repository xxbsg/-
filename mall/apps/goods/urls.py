from django.conf.urls import url

from goods import views
from goods.views import HotSKUListAPIView, SKUListAPIView

urlpatterns=[
    url(r'^categories/(?P<category_id>\d+)/hotskus/$',HotSKUListAPIView.as_view()),

    url(r'^categories/(?P<category_id>\d+)/skus/$', SKUListAPIView.as_view()),

    url(r'^goodslist/$',views.GoodsListAPIView.as_view()),
    #http://api.meiduo.site:8000/goods/skus/16/comments/
    url(r'^skus/(?P<goodsid>\d+)/comments/$',views.GoodsCommentsAPIView.as_view())
]

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('search',views.SKUSearchViewSet,base_name='skus_search')
urlpatterns += router.urls