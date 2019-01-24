from django_redis import get_redis_connection
from rest_framework import serializers

# 因为没有模型，就是用Serializer
class RegisterSmscodeSerializer(serializers.Serializer):
    # 用户输入验证码
    text=serializers.CharField(max_length=4,min_length=4,required=True)
    image_code_id=serializers.UUIDField(required=True)
    """
    序列化验证四种类型：
    1.字段类型
    2.字段选项
    3.单个字段
    4.多个字段


    http://127.0.0.1:8000/verifications/smscodes/18939144593/?text=wxpv&image_code_id=e794aae4-fa8d-4da0-8443-c2b264e0826a
    """

    def validate(self, attrs):
        #1.获取用户提交的验证码
        text = attrs.get('text')
        #2.获取redis的验证码
        # 2.1　连接redis
        redis_conn=get_redis_connection('code')
        # 2.2　获取数据
        image_id=attrs.get('image_code_id')
        redis_text=redis_conn.get('img_'+str(image_id))
        # 2.3　redis的数据有效时期
        if redis_text is None:
            raise serializers.ValidationError('图片验证码过期')
        #3.比对
        # redis的数据是bytes类型
        if redis_text.decode().lower() != text.lower():
            raise serializers.ValidationError('输入错误')
        return attrs