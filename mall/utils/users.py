import re

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    user=None,jwt验证成功之后的user
    request=None  请求
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }

from django.contrib.auth.backends import ModelBackend
from rest_framework.mixins import CreateModelMixin
"""
１．定义一个方法
２．把要抽取的代码复制过去，哪里有问题改哪里　没有的变量定义为参数
３．验证

"""
def get_user_by_account(username):
    try:
        if re.match(r'1[3-9]\d{9}', username):
            # 手机号
            user = User.objects.get(mobile=username)
        else:
            # 用户名
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    return user


class UsernameMobleModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 1.根据用户名确认用户输入的是手机号还是用户名
        # try:
        #     if re.match(r'1[3-9]\d{9}',username):
        #         # 手机号
        #         user = User.objects.get(mobile=username)
        #     else:
        #         # 用户名
        #         user = User.objects.get(username=username)
        # except User.DoesNotExist:
        #     user = None
        user = get_user_by_account(username)
        # 2.验证用户密码
        if user is not None and user.check_password(password):
            return user
        # 3.必须返回数据
        return None



# 扩展
class MyBackend(object):
    def authenticate(self,request,username=None,password=None):
        user = get_user_by_account(username)
        if user is not None and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None