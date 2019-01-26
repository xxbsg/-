from django_redis import get_redis_connection
from rest_framework import serializers

from oauth.models import OAuthQQUser, OAuthSinaUser
from oauth.utils import check_access_token
from users.models import User

"""
手机号，密码，短信验证码和加密的openid这些数据进行效验
效验没有问题　保存数据的时候　是保存的user和openid
"""
class OAuthQQUserSerializer(serializers.Serializer):
    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')

    def validate(self, attrs):
        # 1.需要对加密的openid进行处理
        access_token = attrs.get('access_token')
        openid = check_access_token(access_token)
        if openid is None:
            raise serializers.ValidationError('openid错误')

        # 我们通过sttrs来传递数据
        attrs['openid'] = openid

        # 2.需要对短信进行验证
        # 2.1获取用户提交的
        mobile = attrs.get('mobile')
        sms_code = attrs['sms_code']
        # 2.2　获取redis
        redis_conn = get_redis_connection('code')
        redis_code = redis_conn.get('sms_'+ mobile)
        if redis_code is None:
            raise serializers.ValidationError('短信验证码已过期')
        # 最号删除短信
        redis_conn.delete('sms_'+mobile)
        # 2.3 比对
        if redis_code.decode() != sms_code:
            raise serializers.ValidationError('验证码不一致')
        # 3.需要对手机号进行判断
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 说明用户没有注册过　创建用户
            # User.objects.create()
            pass
        else:
            # 说明注册过，需要对密码进行验证
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError('密码不正确')

            attrs['user'] = user

        return attrs

    # data－－>attrs-->validated_data
    def create(self, validated_data):
        user = validated_data.get('user')
        if user is None:
            # 创建user
            user = User.objects.create(
                mobile = validated_data.get('mobile'),
                username = validated_data['mobile'],
                password = validated_data['password']
            )
            # 对password进行加密
            user.set_password(validated_data['password'])
            user.save()

        qquser = OAuthQQUser.objects.create(
            user=user,
            openid=validated_data['openid']
        )
        return qquser

class OAuthSinaUserSerializer(serializers.Serializer):
    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')

    def validate(self, attrs):
        # 1.需要对加密的openid进行处理
        access_token = attrs.get('access_token')
        openid = check_access_token(access_token)
        if openid is None:
            raise serializers.ValidationError('openid错误')

        # 我们通过sttrs来传递数据
        attrs['openid'] = openid

        # 2.需要对短信进行验证
        # 2.1获取用户提交的
        mobile = attrs.get('mobile')
        sms_code = attrs['sms_code']
        # 2.2　获取redis
        redis_conn = get_redis_connection('code')
        redis_code = redis_conn.get('sms_'+ mobile)
        if redis_code is None:
            raise serializers.ValidationError('短信验证码已过期')
        # 最号删除短信
        redis_conn.delete('sms_'+mobile)
        # 2.3 比对
        if redis_code.decode() != sms_code:
            raise serializers.ValidationError('验证码不一致')
        # 3.需要对手机号进行判断
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 说明用户没有注册过　创建用户
            # User.objects.create()
            pass
        else:
            # 说明注册过，需要对密码进行验证
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError('密码不正确')

            attrs['user'] = user

        return attrs

    # data－－>attrs-->validated_data
    def create(self, validated_data):
        user = validated_data.get('user')
        if user is None:
            # 创建user
            user = User.objects.create(
                mobile = validated_data.get('mobile'),
                username = validated_data['username'],
                password = validated_data['password']
            )
            # 对password进行加密
            user.set_password(validated_data['password'])
            user.save()

        qquser = OAuthSinaUser.objects.create(
            user=user,
            access_token=validated_data['openid']
        )
        return qquser