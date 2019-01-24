from django.conf.urls import url

from goods import views
from goods.views import HotSKUListAPIView, SKUListAPIView

urlpatterns=[
    url(r'^categories/(?P<category_id>\d+)/hotskus/$',HotSKUListAPIView.as_view()),

    url(r'^categories/(?P<category_id>\d+)/skus/$', SKUListAPIView.as_view()),
]

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('search',views.SKUSearchViewSet,base_name='skus_search')
urlpatterns += router.urls