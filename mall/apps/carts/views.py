import base64
import pickle

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView

from carts.serializers import Cartserializer, CartSKUSerializer, CartDeleteSerializer
from goods.models import SKU

"""
POST  　cart/　   新增购物车数据
GET     cart/     获取购物车数据
PUT　　　cart/    修改购物车数据
DELETE   cart/    删除购物车数据
"""
class CartAPIView(APIView):
    # 重写perform_authentication()方法，此方法是REST framework检查用户身份的方法
    def perform_authentication(self, request):
        pass

    """
    添加购物车的业务逻辑是:
    用户点击 添加购物车按钮的时候,前端需要收集数据:
    商品id,个数,选中状态默认为True,用户信息

    1.接收数据
    2.校验数据(商品是否存在,商品的个数是否充足)
    3.获取校验之后的数据
    4.获取用户信息
    5.根据用户的信息进行判断用户是否登陆
    6.登陆用户保存在redis中
        6.1 连接redis
        6.2 将数据保存在redis中的hash 和 set中
        6.3 返回相应
    7.未登录用户保存在cookie中
        7.1 先获取cookie数据
        7.2 判断是否存在cookie数据
        7.3 如果添加的购物车商品id存在 则进行商品数量的累加
        7.4 如果添加的购物车商品id不存在 则直接添加商品信息
        7.5 返回
    """

# 增加
    def post(self,request):

        # 1.接收数据
        data = request.data
        # 2.校验数据(商品是否存在,商品的个数是否充足)
        serializer = Cartserializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3.获取校验之后的数据
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']
        selected = serializer.validated_data['selected']
        # 4.获取用户信息
        try:
            user = request.user
        except Exception as e:
            user = None
        # 5.根据用户的信息进行判断用户是否登陆
        # request.user.is_authenticated
        if user is not None and user.is_authenticated:
            # 6.登陆用户保存在redis中
            #     6.1 连接redis
            redis_conn = get_redis_connection('cart')
            # #     6.2 将数据保存在redis中的hash 和 set中
            #
            # # 应该设置累加数据
            # # redis_conn.hset('cart_%s' %user.id, sku_id, count)
            # redis_conn.hincrby('cart_%s'%user.id,sku_id,count)
            # if selected:
            #     redis_conn.sadd('cart_selected_%s'%user.id,sku_id)


            # 1.创建管道
            pl = redis_conn.pipeline()
            # 2.将指令添加到管道中
            pl.hincrby('cart_%s'%user.id,sku_id,count)
            if selected:
                pl.sadd('cart_selected_%s'%user.id,sku_id)
            # 3.执行管道
            pl.execute()



            #     6.3 返回相应
            return Response(serializer.data)

        else:
            # 7.未登录用户保存在cookie中
            #     7.1 先获取cookie数据
            cookie_str = request.COOKIES.get('cart')
            #     7.2 判断是否存在cookie数据
            if cookie_str is not None:
                # 说明有数据　对base64数据进行解码
                decode = base64.b64decode(cookie_str)
                # 将二进制转换为字典
                cookie_cart = pickle.loads(decode)
            else:
                # 说明没有数据　　初始化
                cookie_cart = {}
            #     7.3 如果添加的购物车商品id存在 则进行商品数量的累加
            # cookie_cart = {sku_id: {count:xxx,selected:xxx}}
            if sku_id in cookie_cart:
                # 存在　　原个数
                origin_count = cookie_cart[sku_id]['count']
                # 现个数
                count += origin_count
            #     7.4 如果添加的购物车商品id不存在 则直接添加商品信息
            cookie_cart[sku_id] = {
                'count':count,
                'selected':selected
            }
            #     7.5 对字典进行处理
            #     7.5.1 将字典转化为二进制
            dumps = pickle.dumps(cookie_cart)
            #     7.5.2　进行base64的编码
            dd = base64.b64encode(dumps)
            #     7.5.3 　将bytes类型转化为字符串
            value = dd.decode()
            # 7.6 返回响应
            response = Response(serializer.data)
            response.set_cookie('cart',value)
            return response

    """
查询购物车数据

    1.接收用户信息
    2.根据用户信息进行判断
    3.登陆用户从redis中获取数据
        3.1 连接redis
        3.2 将数据保存到redis中得hash和set中
            hash cart_userid: {sku_id:count}
            set cart_selected_userid: sku_id
            获取hash的所有数据[sku_id,sku_id]
    4.未登陆用户从cookie中获取数据
        4.1 先从cookie中获取数据
        4.2 判断是否存在购物车数据
            {sku_id:{count:xxx,selected:xxxx}}
            [sku_id,sku_id]
    5 根据商品id,获取商品的详细信息
    6 返回相应
    """
# 查询
    def get(self,requerst):
        # 1.接收用户信息
        try:
            user = requerst.user
        except Exception as e:
            user = None
        # 2.根据用户信息进行判断
        # requerst.user.is_authenticated
        if user is not None and user.is_authenticated:
        # 3.登陆用户从redis中获取数据
        #     3.1 连接redis
            redis_conn = get_redis_connection('cart')
        #     3.2 将数据保存到redis中得hash和set中
        #         获取ｈａｓｈ数据
            redis_ids_count = redis_conn.hgetall('cart_%s'%user.id)
        #         获取set数据
            redis_selected_ids = redis_conn.smembers('cart_selected_%s'%user.id)
        #    redis获取的数据是bytes类型　我们将它转换为cookie的数据格式
            cookie_cart = {}
            for sku_id,count in redis_ids_count.items():
                cookie_cart[int(sku_id)] = {
                    'count':int(count),
                    'selected':sku_id in redis_selected_ids
                }

        else:
        # 4.未登陆用户从cookie中获取数据
        #     4.1 先从cookie中获取数据
            cookie_str = requerst.COOKIES.get('cart')
        #     4.2 判断是否存在购物车数据
            if cookie_str is not None:
                # 将base64数据进行解码二进制并转化为字典
                cookie_cart = pickle.loads(base64.b64decode(cookie_str))
            else:
                cookie_cart = {}
        #         {sku_id:{count:xxx,selected:xxxx}}
        #         [sku_id,sku_id]
        # 5 根据商品id,获取商品的详细信息
        ids = cookie_cart.keys()
        skus = SKU.objects.filter(pk__in=ids)
        # 对商品列表数据进行遍历，来动态添加count和选中状态
        for sku in skus:
            sku.count = cookie_cart[sku.id]['count']              #   sku.id   int
            sku.selected = cookie_cart[sku.id]['selected']
        # 6 返回相应
        serializer = CartSKUSerializer(skus,many=True)
        return Response(serializer.data)

    """
修改购物车数据　　ＰＵＴ
    前端需要将商品id count（个数采用的是最终数量提交给后端），selected提交给后端
    1.接收数据
    2.校验数据
    3.获取验证之后的数据
    4.获取用户信息
    5.根据用户的登陆状态进行判断
    6.登陆用户redis
        6.1 连接redis
        6.2 更新数据
        6.3 返回相应
    7.未登录用户cookie
        7.1 获取cookie数据
        7.2 判断cart数据是否存在
        7.3 更新数据
        7.4 返回相应
    """
# 修改
    def put(self,request):
        # 1.接收数据
        data = request.data
        # 2.校验数据
        serializer = Cartserializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3.获取验证之后的数据
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']
        selected = serializer.validated_data['selected']
        # 4.获取用户信息
        try:
            user = request.user
        except Exception as e:
            user = None
        # 5.根据用户的登陆状态进行判断
        if user is not None and user.is_authenticated:
        # 6.登陆用户redis
        #     6.1 连接redis
            redis_conn = get_redis_connection('cart')
        #     6.2 更新数据
            # hash
            redis_conn.hset('cart_%s'%user.id,sku_id,count)
            # set
            if selected:
                # 选中添加到set中
                redis_conn.sadd('cart_selected_%s'%user.id,sku_id)
            else:
                # 取消选中，应该删除
                redis_conn.srem('cart_selected_%s'%user.id,sku_id)
        #      6.3 返回相应
        # 必须要将数据返回回去
        # 因为前端是将 个数的终值 传递过来的,我们要返回回去
            return Response(serializer.data)
        # 7.未登录用户cookie
        #     7.1 获取cookie数据
        cookie_str = request.COOKIES.get('cart')
        #     7.2 判断cart数据是否存在
        if cookie_str is not None:
            # 将base64数据进行解码成二进制并转化为字典
            cookie_cart = pickle.loads(base64.b64decode(cookie_str))
        else:
            cookie_cart = {}
        #     7.3 更新数据
        if sku_id in cookie_cart:
            cookie_cart[sku_id] = {
                'count':count,
                'selected':selected
            }
        #     7.4 返回相应
        response = Response(serializer.data)
        value = base64.b64encode(pickle.dumps(cookie_cart)).decode()
        response.set_cookie('cart',value)
        return response

    """
删除购物车数据
           用户在删除购物车数据的时候,只需要将商品的id传递给我们就可以

           1.后端接收数据
           2.校验数据
           3.获取校验之后的数据
           4.获取用户信息
           5.根据用户信息进行判断
           6.登陆用户redis
               6.1 连接redis
               6.2 删除数据
               6.3 返回相应
           7.未登录用户cookie
               7.1 获取cookie数据
               7.2 判断cart数据是否存在
               7.3 删除指定数据
               7.4 返回相应
           """
# 删除
    def delete(self,request):
        # 1.后端接收数据
        data = request.data
        # 2.校验数据
        serializer =CartDeleteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3.获取校验之后的数据
        sku_id = serializer.validated_data['sku_id']
        # 4.获取用户信息
        try:
            user = request.user
        except Exception as e:
            user = None
        # 5.根据用户信息进行判断
        # request.user.is_authenticated
        if user is not None and user.is_authenticated:
        # 6.登陆用户redis
        #     6.1 连接redis
            redis_conn = get_redis_connection('cart')
        #     6.2 删除数据
            redis_conn.hdel('cart_%s'%user.id,sku_id)
            redis_conn.srem('cart_selected_%s'%user.id,sku_id)
        #     6.3 返回相应
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
        # 7.未登录用户cookie
            cookie_str = request.COOKIES.get('cart')
        #     7.1 获取cookie数据
        #     7.2 判断cart数据是否存在
            if cookie_str is not None:
                cookie_cart = pickle.loads(base64.b64decode(cookie_str))
            else:
                cookie_cart = {}
        #     7.3 删除指定数据
        if sku_id in cookie_cart:
            del cookie_cart[sku_id]
        #     7.4 返回相应
        response = Response(status=status.HTTP_204_NO_CONTENT)
        value = base64.b64encode(pickle.dumps(cookie_cart)).decode()
        response.set_cookie('cart',value)
        return response
