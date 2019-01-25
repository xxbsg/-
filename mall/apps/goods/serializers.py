from drf_haystack.serializers import HaystackSerializer
from rest_framework import serializers

from goods.models import SKU
from goods.search_indexes import SKUIndex
from orders.models import OrderInfo


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


class GoodsListSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderInfo
        fields = ('order_id','total_count','total_amount','pay_method','status','create_time',)