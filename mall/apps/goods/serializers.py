from drf_haystack.serializers import HaystackSerializer
from rest_framework import serializers

from goods.models import SKU
from goods.search_indexes import SKUIndex


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