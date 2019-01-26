from django.conf.urls import url

from .views import PlaceOrderAPIView, OrderAPIView, CommentAPIView, GoodsJudgeAPIView, CommentDetailAPIView

urlpatterns=[

    url(r'^places/$',PlaceOrderAPIView.as_view()),
    url(r'^$',OrderAPIView.as_view(),name='order'),
    # url(r'^$',OrderListAPIView.as_view()),

    # 更新评论
    # http://api.meiduo.site:8000/orders/20190125121520000006/comments/
    url(r'^(?P<order_id>\d+)/comments/$', CommentAPIView.as_view()),
    # 评论界面显示
    url(r'^(?P<order_id>\d+)/uncommentgoods/$', GoodsJudgeAPIView.as_view()),
    # 评论详情
    url(r'^skus/(?P<sku_id>\d+)/comments/$', CommentDetailAPIView.as_view())
]