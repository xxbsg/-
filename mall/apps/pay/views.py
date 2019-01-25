from alipay import AliPay
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from mall import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import OrderInfo

"""
1. 第一步：创建应用 (创建appid)
2. 第二步：配置密钥 (2对 我们的服务器一对,支付宝的一对)
    2.1 我们生成的公钥和私钥  私钥放在我们自己服务器上
            公钥放在 支付宝的平台上
    2.2 把支付宝的公钥复制下来, 需要放到一个 以 ---public begin---  ---end-- 的文件中


3. 第三步：搭建和配置开发环境 (下载/安装 SDK) (SDK 就是 支付宝封装好的库)
4. 第四步：接口调用(开发, 看支付宝的API(接口文档))
买家账号axirmj7487@sandbox.com
登录密码111111

"""
"""
当用户点击去支付的时候,需要让前端将订单id传递过来

该接口必须是登陆用户

1. 接收订单id
2. 根据订单id查询订单
3. 生成alipay实例对象
4. 调用支付接口生成order_string
5. 拼接url
6. 返回url

GET /orders/(?P<order_id>\d+)/payment/
"""

class PaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,order_id):
        # 1. 接收订单id
        user = request.user
        # 2. 根据订单id查询订单
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 3. 生成alipay实例对象

        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()

        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2" , # RSA 或者 RSA2
            debug = settings.ALIPAY_DEBUG  # 默认False
            )
        # 4. 调用支付接口生成order_string
        subject = "测试订单"

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject=subject,
            return_url="http://www.meiduo.site:8080/pay_success.html",
            # notify_url="https://example.com/notify"  # 可选, 不填则使用默认notify url
            )
        # 5. 拼接url
        alipay_url = settings.ALIPAY_URL + '?' + order_string
        # 6. 返回url
        return Response({'alipay_url':alipay_url})