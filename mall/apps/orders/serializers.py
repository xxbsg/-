from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU
from goods.serializers import SKUIndexSerializer, HotSKUListSerializer
from orders.models import OrderInfo, OrderGoods


class OrderSKUSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(label='个数',read_only=True)

    class Meta:
        model = SKU
        fields = ('id','name','count','default_image_url','price')

class OrderPlaceSerializer(serializers.Serializer):

    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = OrderSKUSerializer(many=True)
from rest_framework import serializers
from django.db import transaction
class og(serializers.ModelSerializer):
    sku = HotSKUListSerializer()
    class Meta:
        model=OrderGoods
        fields='__all__'
class ddanxlh(serializers.ModelSerializer):
    skus=og(many=True)

    class Meta:
        model=OrderInfo

        # fields=['skus','freight',]
        fields='__all__'

class OrderSerializer(serializers.ModelSerializer):
    # set_OrderGoods=OrderGoodsSerializer(many=True,write_only=True)
    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        # 系统提供的create方法不能满足我们的需求，我们需要去重写

        """
        当用户点击提交订单按钮的时候，我们需要生成订单信息，在生成订单列表(商品)信息

         1.生成订单信息
              1.1 获取user信息
              1.2 获取地址信息
              1.3 获取支付方式
              1.4 判断支付状态
              1.5 订单id(订单id我们采用自己生成的方式)
              1.6 运费,价格和数量 先为 0
              order = OrderInfo.objects.create()

          2.生成订单商品(列表)信息
            2.1 连接redis
            2.2  hash
                 set
            2.3  选中商品的信息  {sku_id:count}
            2.4  [sku_id,sku_id,...]
            2.5  [SKU,SKU,SKU]
            2.6 对列表进行遍历

                SKU
                判断库存

                减少库存
                添加销量

                累加 计算总数量和总价格

                生成OrderGoods信息
        """

        # 1.生成订单信息
        #      1.1 获取user信息
        user = self.context['request'].user
        #      1.2 获取地址信息
        address = validated_data['address']
        #      1.3 获取支付方式
        pay_method = validated_data['pay_method']
        #      1.4 判断支付状态

        # if pay_method == 1:
        #     status = 1   # 货到付款
        # else:
        #     status = 2   # 支付宝
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            # 货到付款
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        #      1.5 订单id(订单id我们采用自己生成的方式)
        # 时间(年月日十分秒)　＋　６位的用户id信息
        from django.utils import timezone
        order_id = timezone.now().strftime('%Y%m%d%H%M%S')+ '%06d'%user.id
        #      1.6 运费10,价格和数量 先为 0
        from decimal import Decimal
        freight = Decimal('10.00')
        total_count = 0
        total_amount = Decimal('0')
        # with语法对部分代码实现事务功能
        with transaction.atomic():

            # 事务回滚点
            save_point = transaction.savepoint()

            order = OrderInfo.objects.create(
                order_id = order_id,
                user = user,
                address = address,
                total_count = total_count,
                total_amount = total_amount,
                freight = freight,
                pay_method = pay_method,
                status = status
            )


            #  2.生成订单商品(列表)信息
            #    2.1 连接redis
            redis_conn = get_redis_connection('cart')
            #    2.2  hash
            redis_id_count = redis_conn.hgetall('cart_%s'%user.id)
            #         set
            redis_selected_ids = redis_conn.smembers('cart_selected_%s'%user.id)
            #    2.3  选中商品的信息  {sku_id:count}
            # 组织一个选中商品的信息　　selected_cart = {sku_id:count}
            selected_cart = {}
            for sku_id in redis_selected_ids:
                selected_cart[int(sku_id)] = int(redis_id_count[sku_id])
            #    2.4  [sku_id,sku_id,...]
            ids = selected_cart.keys()
            #    2.5  [SKU,SKU,SKU]
            skus = SKU.objects.filter(pk__in=ids)
            #    2.6 对列表进行遍历
            for sku in skus:
                # 购买的数量
                count = selected_cart[sku.id]
                if sku.stock<count:

                    # 出现异常就会滚，回滚到指定的保存点
                    transaction.savepoint_rollback(save_point)

                    raise serializers.ValidationError('库存不足')
        #        SKU
        #        判断库存
        #        减少库存
        #        添加销量
        #         import time
        #         time.sleep(10)
                # sku.stock -= count
                # sku.sales += count
                # sku.save()

                # 用乐观锁来实现
                # １．先记录库存
                old_stock = sku.stock
                old_sales = sku.sales
                # ２．吧跟新的数据准备出来
                new_stock = sku.stock - count
                new_sales = sku.sales + count
                # 3. 跟新数据的时候再查询一次　是否和　之前的记录一致
                rect = SKU.objects.filter(pk=sku.id,stock=old_stock).update(stock=new_stock,sales=new_sales)

                if rect == 0:
                    print('下单失败')
                    transaction.savepoint_rollback(save_point)
                    raise serializers.ValidationError('下单失败')

        #        累加 计算总数量和总价格
                order.total_count += count
                order.total_amount += (count * sku.price)
        #        生成OrderGoods信息
                OrderGoods.objects.create(
                    order = order,
                    sku = sku,
                    count = count,
                    price = sku.price
                )

            # 保存订单信息
            order.save()

            # 如果没有问题　提交事务就可以
            transaction.savepoint_commit(save_point)

        # 生成订单之后,一定要注册 删除 购物车选中的内容
        pl = redis_conn.pipeline()
        pl.hdel('cart_%s' % user.id, *redis_selected_ids)
        pl.srem('cart_selected_%s' % user.id, *redis_selected_ids)

        pl.execute()
        return order


