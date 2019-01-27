import re

from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from users.models import User


class AdminLoginSerializer(serializers.Serializer):
    """后台登录序列化器"""
    username = serializers.CharField(label='用户名',max_length=20,required=True)
    password = serializers.CharField(label='密码',max_length=20,min_length=8,required=True)

    def validate(self, attrs):
        # 获取数据
        username = attrs.get('username')
        password = attrs.get('password')
        # 数据库查询数据
        user = User.objects.get(username=username)
        is_superuser = user.is_superuser
        # 校验密码
        if not user.check_password(password):
            raise serializers.ValidationError('密码错误')
        # 校验用户权限
        if is_superuser is not True:
            raise serializers.ValidationError('用户权限不够')
        attrs['user']=user
        # 返回
        return attrs


class AdminUserSerializer(serializers.ModelSerializer):
    """后台新增用户序列化器"""

    class Meta:
        model=User
        fields=('username','password','mobile','email')
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {
                'max_length': 20,
                'min_length': 5,
                'error_messages': {
                    'min_length': '用户名不能低于5字符',
                    'max_length': '用户名不能超过20字符',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '密码不能低于8字符',
                    'max_length': '密码不能高于20字符',
                }
            }
        }

    # 手机号格式验证
    def validate_mobile(self, value):
        if not re.match(r'1[3-9]\d{9}', value):
            raise serializers.ValidationError('手机号格式不正确')
        return value


    # 邮箱格式验证
    def validate_email(self, value):
        if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', value):
            raise serializers.ValidationError('邮箱格式错误')
        return value


    # 重写create方法
    def create(self, validated_data):
        user = super().create(validated_data)
        # 对密码进行加密
        user.set_password(validated_data['password'])
        user.save()

        return user

