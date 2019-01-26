# verifications　　验证
import random
import re

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework import request
from rest_framework.views import APIView

from celery_tasks.sms.tasks import send_sms_code
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection

from libs.yuntongxun.sms import CCP
from oauth.utils import generic_open_id
from users.models import User
from verifications import constants

from verifications.serializers import RegisterSmscodeSerializer, ValidateSmsCodeSerializer

"""
前端传递一个uuid过来　　我们后端生成一个图片
1.接受image_code_id
2.生成图片和验证码
3.吧验证码保存到redis中
4.返回图片响应

GET  /verifications/imagecodes/(?P<image_code_id>.+)/
GET  /verifications/imagecodes/?image_code_id=xxxx

"""
class RegisterImageAPIView(APIView):
    def get(self,request,image_code_id):
        # 1.接受image_code_id
        # 2.生成图片和验证码
        text,image = captcha.generate_captcha()
        # 3.吧验证码保存到redis中
            # 3.1连接redis
        redis_conn = get_redis_connection('code')
            # 3.2设置redis
        redis_conn.setex('img_'+image_code_id,60,text)
        # 4.返回图片响应
        # 注意,图片是二进制,我们通过HttpResponse返回
        return HttpResponse(image,content_type='image/jpeg')

    """
    1.分析需求(到底要干什么)
    2.把需要做的事情写下来(把思路梳理清楚)
    3.请求方式　　路由
    4.确定视图
    5.按照步骤实现功能

    当用户点击　获取短信按钮的时候　前端应该将手机号，图片验证码以及验证码id发送给后端

    1.接受参数
    2.效验参数
    3.生成短信
    4.将短信保存到redis中
    5.使用云通讯发送短信
    6.返回响应

    GET  /verifications/smscodes/(?P<mobile>1[345789]\d{9})/?text=xxxx & image_code_id=xxx
    一种是路由weather/beijing/2018/
    另一中是查询字符串weather/?place=beijing&year=2018
    混合起来也是可以的　weather/2018/?place=beijing
    """
    # APIView        基类
    # GenericAPIView    对列表视图和详情视图做了通用支持，一般和mixin配合使用
    # ListAPIView,RetrieveAPIView   封装好了的

class RegisterSmscodeAPIView(APIView):
    def get(self,request,mobile):

        # 1.接受参数
        params=request.query_params
        # 2.效验参数
        # 还需要验证码用户输入的图片验证码和redis的保存是否一致　
        serializer=RegisterSmscodeSerializer(data=params)
        serializer.is_valid(raise_exception=True)


        # 3.生成短信
        sms_code = '%06d'%random.randint(0, 999999)
        print(sms_code)
        # 4.将短信保存到redis中
        redis_conn = get_redis_connection('code')
        redis_conn.setex('sms_' + mobile,5*60,sms_code)
        # 5.使用云通讯发送短信
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)

        from celery_tasks.sms.tasks import send_sms_code
        # 必须调用delay方法;delay的参数和任务的参数对应
        send_sms_code.delay(mobile,sms_code)

        # 6.返回响应
        return Response({'msg':'ok'})


###################################用户忘记密码重置获取手机号视图#########################################
class UserForgetPasswordAPIView(APIView):
    """
    用户忘记密码重置获取手机号视图
    GET  '/verifications/' + this.username + '/sms/token/?text='+ this.image_code + '&image_code_id=' + this.image_code_id
    """
    def get(self,request,username):
        # 获取数据
        data = request.query_params
        serializer = RegisterSmscodeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            if re.match(r'1[3-9]\d{9}', username):
                user = User.objects.get(mobile=username)
            else:
                user = User.objects.get(username=username)
        except Exception as e:
            user=None
        if user is not None:
            mobile = user.mobile
            # 生成token
            num = '%10d'%random.randint(0,9999999999)
            token=generic_open_id(num)
            # 将token保存在redis中
            redis_conn=get_redis_connection('code')
            redis_conn.setex('%s'%token,constants.TOKEN_CODE_EXPIRE_TIME,mobile)
            mobile_1 = mobile[0:3] + '****' + mobile[7:11]
            return Response({
                'mobile':mobile_1,
                'access_token':token
            })
        else:
            return Response({'message':'用户不存在'},status=404)

###########################发送手机验证码###################################################
class SendSmsCodeAPIView(APIView):
    """
    发送手机验证码
    GET   /sms_codes/?access_token='+ this.access_token
    """
    def get(self,request):
        access_token = request.query_params.get('access_token')
        # 连接redis
        redis_conn = get_redis_connection('code')
        mobile = redis_conn.get(access_token).decode()
        if mobile:
            # 生成短信验证码
            sms_code = '%06d' % random.randint(0, 999999)
            send_sms_code(mobile, sms_code)
            # 短信验证码保存在redis中
            redis_conn.setex('sms_' + mobile, constants.SMS_CODE_EXPIRE_TIME, sms_code)
            redis_conn.setex('sms_flag_' + mobile, 60, 1)
            # 返回响应
            return Response({'message':'OK'})
        else:
            return Response({'message':'该界面已过期'},status=400)


##############################验证短信验证码，返回access_token###############################################
class ValidateSmsCodeAPIView(APIView):
    """
    验证短信验证码，返回access_token
    GET /verifications/' + this.username + '/password/token/?sms_code=' + this.sms_code
    """
    def get(self,request):
        # 接收数据
        params = request.query_params
        username=params.get('username')
        # 验证数据
        serializer=ValidateSmsCodeSerializer(data=params)
        serializer.is_valid(raise_exception=True)
        try:
            if re.match(r'1[3-9]\d{9}', username):
                user = User.objects.get(mobile=username)
            else:
                user = User.objects.get(username=username)
        except Exception as e:
            user=None
        if user is not None:
            # 生成token
            num = '%10d' % random.randint(0, 9999999999)
            token = generic_open_id(num)
            # 将token保存在redis中
            redis_conn = get_redis_connection('code')
            redis_conn.setex('%s' % user.id, constants.TOKEN_CODE_EXPIRE_TIME, token)
            # 返回响应
            return Response({
                'user_id':user.id,
                'access_token':token
            })
        else:
            return Response({'message':'用户不存在'},status=404)
