from decimal import Decimal
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from orders.serializers import OrderSKUSerializer, OrderSerializer, OrderPlaceSerializer

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
from rest_framework.generics import CreateAPIView
class OrderAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer