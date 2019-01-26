from drf_haystack.serializers import HaystackSerializer
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from goods.models import SKU
from goods.search_indexes import SKUIndex
from orders.models import OrderInfo, OrderGoods


class HotSKUListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields =  ('id', 'name', 'price', 'default_image_url', 'comments')

class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    class Meta:
        index_classes = [SKUIndex]
        fields = ('text','id','name','price','default_image_url','comments')

class OrderGoodsSerializer(serializers.ModelSerializer):

    sku = HotSKUListSerializer()
    class Meta:
        model = OrderGoods
        fields = '__all__'

class GoodsListSerializer(serializers.ModelSerializer):

    skus = OrderGoodsSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = ('order_id','total_count','total_amount','pay_method','status','create_time','skus','freight')