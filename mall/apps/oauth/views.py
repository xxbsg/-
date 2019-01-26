import webbrowser

from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ

from libs import sinaweibopy3
from mall import settings
from oauth.models import OAuthQQUser, OAuthSinaUser
from oauth.serializers import OAuthQQUserSerializer, OAuthSinaUserSerializer
from oauth.utils import generic_open_id

"""
当用户点击ｑｑ按钮的时候，回发送一个请求
我们后端返回给他一个url（url是根据文档拼接出来的）
GET    /oauth/qq/status/
"""

class OAuthQQURLAPIView(APIView):
    def get(self,request):
        state = '/'
        # 1.创建oauthqq的实例对象
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state=state
        )
        # 2.获取跳转的url
        auth_url = oauth.get_qq_url()
        return Response({'auth_url':auth_url})
        # return Response({'auth_url': 'http://www.itcast.cn'})

"""
1.当用户同意授权登录这个时候会返回一个code
2.我们用ｃｏｄｅ换取token
3.有了token 我们再获取openid
"""
"""
1.分析需求 (到底要干什么)
2.把需要做的事情写下来(把思路梳理清楚)
3.路由和请求方式
4.确定视图
5.按照步骤实现功能

前段接受到用户的同意之后，前端应该奖这个code发送给后端
1.后端接受数据
2.用code换ｔｏｋｅｎ
3.用token 换openid

GET   /oauth/qq/users/?code=xxxx
"""


class OAuthQQUserAPIView(APIView):
    def get(self,request):

        # 1.后端接受数据
        params = request.query_params
        code = params.get('code')
        if code is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # 2.用code换ｔｏｋｅｎ
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                client_secret=settings.QQ_CLIENT_SECRET,
                redirect_uri=settings.QQ_REDIRECT_URI)
        token = oauth.get_access_token(code)
        # 'EDBEC8459930A5A697736542BDC820FB'
        # https://graph.qq.com/oauth2.0/me?access_token=EDBEC8459930A5A697736542BDC820FB
        # 3.用token 换openid
        openid = oauth.get_open_id(token)


        """
        openid 是此网站上唯一对应用户身份的标示，网站可将此ＩＤ进行储存便于用户下次登陆时辨识其身份
        获取openid有两种情况
            1.用户之前绑定过
            2.用户之前没有绑定过
        """
        # 第一种
        # 根据openid查询数据
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            #  不存在
            # openid很重要，我们需要对openid进行一个处理
            # 绑定应该有一个时效
            """
            封装和抽取的步骤
            1. 定义一个函数
            2. 将要抽取的代码 复制过来 哪里有问题改哪里 没有的变量定义为参数
            3. 验证
            """
            # s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
            #
            # # 2. 组织数据
            # data = {
            #     'openid': openid
            # }
            #
            # # 3. 让序列化器对数据进行处理
            # token = s.dumps(data)

            token = generic_open_id(openid)
            return Response({'access_token':token})

        else:
            # 存在，应该让用户登录
            from rest_framework_jwt.settings import api_settings

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(qquser.user)
            token = jwt_encode_handler(payload)

            return Response({
                'token':token,
                'username':qquser.user.username,
                'user_id':qquser.user.id
            })


    """
    第二种
    绑定：
    当用户点击绑定的时候，我们需要将手机号，密码，短信验证码和加密的openid传递过来
    1.接受数据
    2.对数据进行效验
    3.保存数据
    4.返回响应

    POST   /oauth/qq/users/
    """
    def post(self,request):
        # 1.接受数据
        data = request.data
        # 2.对数据进行效验
        serializer = OAuthQQUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3.保存数据
        qquser = serializer.save()
        # 4.返回响应   应该有token数据
        from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(qquser.user)
        token = jwt_encode_handler(payload)

        return Response({
            'token':token,
            'username':qquser.user.username,
            'user_id':qquser.user.id
        })



class OAuthSinaUrlAPIView(APIView):
    def get(self,request):
        # step 1 : sign a app in weibo and then define const app key,app srcret,redirect_url
        APP_KEY = '1084785763'
        APP_SECRET = '49cbfb0acc4dc49b71e4db88c78c9585'
        REDIRECT_URL = 'http://www.meiduo.site:8080/sina_callback.html'
        # step 2 : get authorize url and code
        global client
        client = sinaweibopy3.APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=REDIRECT_URL)
        url = client.get_authorize_url()
        return Response({'auth_url': url})
        # print(url)
class OAuthSinaUserAPIView(APIView):
    def get(self, request):
        # 1.后端接受数据
        params = request.query_params
        code = params.get('code')
        if code is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
            # 2.用code换ｔｏｋｅｎ
        try:
            # APP_KEY = '1084785763'
            # APP_SECRET = '49cbfb0acc4dc49b71e4db88c78c9585'
            # REDIRECT_URL = 'http://www.meiduo.site:8080/sina_callback.html'
            # global client = sinaweibopy3.APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=REDIRECT_URL)
            global client
            result = client.request_access_token(code)  # Enter the CODE obtained in the authorized address
            openid=result.access_token
            # At this point, the access_token and expires_in should be saved,
            # because there is a validity period.A
            # If you need to send the microblog multiple times in a short time,
            # you can use it repeatedly without having to acquire it every time.
            # client.set_access_token(result.access_token, result.expires_in)
            #
            # openid=client.get.account__get_uid()
        except ValueError:
            return Response(status=400)
        try:
            sinauser = OAuthSinaUser.objects.get(access_token=openid)
        except OAuthSinaUser.DoesNotExist:
            #  不存在
            # openid很重要，我们需要对openid进行一个处理
            # 绑定应该有一个时效
            """
            封装和抽取的步骤
            1. 定义一个函数
            2. 将要抽取的代码 复制过来 哪里有问题改哪里 没有的变量定义为参数
            3. 验证
            """
            # s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
            #
            # # 2. 组织数据
            # data = {
            #     'openid': openid
            # }
            #
            # # 3. 让序列化器对数据进行处理
            # token = s.dumps(data)

            token = generic_open_id(openid)
            return Response({'access_token': token})

        else:
            # 存在，应该让用户登录
            from rest_framework_jwt.settings import api_settings

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(sinauser.user)
            token = jwt_encode_handler(payload)

            return Response({
                'token': token,
                'username': sinauser.user.username,
                'user_id': sinauser.user.id
            })

    def post(self, request):
        # 1.接受数据
        data = request.data
        # 2.对数据进行效验
        serializer = OAuthSinaUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3.保存数据
        sinauser = serializer.save()
        # 4.返回响应   应该有token数据
        from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(sinauser.user)
        token = jwt_encode_handler(payload)

        return Response({
            'token': token,
            'username': sinauser.user.username,
            'user_id': sinauser.user.id
        })
