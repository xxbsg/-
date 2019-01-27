from decimal import Decimal
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import mixins

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from goods.serializers import HotSKUListSerializer
from mall import settings

from orders.serializers import OrderSKUSerializer, OrderSerializer, OrderPlaceSerializer, ddanxlh
from utils.pagination import StandardResultsSetPagination

"""
1.我们获取用户信息
２．从redis中获取数据
３．需要获取的是选中的数据
４．[sku_id,sku_id]
5.[SKU,SKU.SKU]
6.返回响应

GET  /orders/placeorders/
"""
class PlaceOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        # 1.我们获取用户信息
        user = request.user
        # ２．从redis中获取数据
        redis_conn = get_redis_connection('cart')
        # hash
        redis_id_count = redis_conn.hgetall('cart_%s'%user.id)
        # set
        selected_ids = redis_conn.smembers('cart_selected_%s'%user.id)
        # ３．需要获取的是选中的数据
        # 同时对bytes类型进行转化
        selected_cart = {}   # {sku_id:count}
        for sku_id in selected_ids:
            selected_cart[int(sku_id)] = int(redis_id_count[sku_id])

        # ４．[sku_id,sku_id]
        ids = selected_cart.keys()
        # 5.[SKU,SKU.SKU]
        skus = SKU.objects.filter(pk__in = ids)
        # 商品个数
        for sku in skus:
            sku.count = selected_cart[sku.id]
        # 6.返回响应
        # serializer = OrderSKUSerializer(skus,many=True)
        # data = {
        #     'freight':10,
        #     'skus':serializer.data
        # }
        freight = Decimal('10.00')
        serializer = OrderPlaceSerializer({
            'freight':freight,
            'skus':skus
        })
        return Response(serializer.data)

"""
提交订单

１．接受前端数据(用户信息，地址，支付方式)
２．验证数据
３．数据入库
４．返回响应
"""
from rest_framework.generics import CreateAPIView, ListAPIView
from .models import OrderInfo, OrderGoods


class OrderAPIView(CreateAPIView):
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    serializer_class = OrderSerializer
    def get(self,request):
        user=request.user
        oderinfos=OrderInfo.objects.filter(user_id=user.id)

        # a=oderinfos.skus.all()
        # # skus = OrderGoods.objects.filter(order_id=oderinfos.order_id)
        # oderinfos.skus = a
        #
        # s=ddanxlh(oderinfos)
        # s.is_valid(raise_exception=True)
        # self.pagination_class=StandardResultsSetPagination
        # data=self.paginator.get_paginated_response(s.data)
        pg = StandardResultsSetPagination()
        pager_roles = pg.paginate_queryset(queryset=oderinfos, request=request, view=self)
        ser = ddanxlh(instance=pager_roles, many=True)
        return pg.get_paginated_response(ser.data)
class shangpin(APIView):
    def get(self,request,odid):
        oderinfos = OrderInfo.objects.get(order_id=odid,is_commented=0)

        s=ddanxlh(oderinfos)
        return Response(s.data.get('skus'))
    
class shangpinpl(APIView):
    def post(self,request,odid):
        data=request.data
        try:
            oderinfos = OrderGoods.objects.get(order_id=odid,sku_id=data.get('sku'))
        except:
            return Response(status=400)
        else:
            oderinfos.comment=data.get('comment')
            oderinfos.is_anonymous = data.get('is_anonymous')
            oderinfos.score = data.get('score')
            oderinfos.is_commented=1
            oderinfos.save()
            goods=OrderGoods.objects.filter(order_id=odid)
            od = OrderInfo.objects.get(order_id=odid)
            pd=[]
            for good in goods:
                pd.append(good.is_commented)
            if all(pd):
               od.status=5
               od.save()

            return Response(status=200)