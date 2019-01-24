from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from areas.models import Area
from areas.serializers import AreaSerializer, SubsAreaSerializer

"""
1. 获取省份信息的时候
select * from tb_areas where parent_id is null;


2. 获取市的信息的时候
3. 获取区县的信息的时候
select * from tb_areas where parent_id=110000;
select * from tb_areas where parent_id=110100;

"""
# class AreaProviceAPIView(APIView):
#     # 获取省份信息
#     def get(self,request):
#         pass
#
# class AreaDistrictAPIView(APIView):
#     # 获取区县信息
#     def get(self,request):
#         pass
# http://127.0.0.1:8000/areas/infos/        省份信息          list 方法

# http://127.0.0.1:8000/areas/infos/110000  市区县信息        retrieve

# 使用缓存：省市区的数据是经常被用户查询使用的，而且数据基本不变化
from rest_framework_extensions.cache.mixins import CacheResponseMixin

class AreaModelViewSet(CacheResponseMixin,ReadOnlyModelViewSet):

    # 让他不使用分页类　　　如果数据不变化，考虑是否有缓存
    pagination_class = None

    def get_queryset(self):
        # 我们可以根据不同的业务逻辑返回不同的数据原
        if self.action == 'list':
            return Area.objects.filter(parent=None)

            # return Area.objects.filter(parent__isNull=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        # 我们可以根据不同的业务逻辑返回不同的序列化器
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubsAreaSerializer

