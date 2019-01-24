# 使用TimedJSONWebSignatureSerializer可以生成带有有效期的token

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature
from mall import settings

# secret_key秘钥
# expires_in=None　过期时间
"""
如果token被篡改了会报BadSignature异常
如果token过期了  会报SignatureExpired异常
"""

"""
为什么要封装和抽取
１.为了解耦和
２.为了方便复用
封装和抽取的原则是什么呢?
            1. 如果第二次出现的代码 就进行封装
            2. 实现了一个小功能

            封装和抽取的步骤
            1. 定义一个函数
            2. 将要抽取的代码 复制过来 哪里有问题改哪里 没有的变量定义为参数
            3. 验证

"""
def generic_open_id(openid):
    # 1.创建序列化器
    s = Serializer(secret_key= settings.SECRET_KEY,expires_in=60*60)
    # 2.对数据进行处理
    token = s.dumps({
        'openid':openid
    })
    # 3.返回
    return token.decode()

def check_access_token(access_token):
    # 1.创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=60*60)
    # 2.对数据进行loads操作
    try:
        data =  s.loads(access_token)

    except BadSignature:
        return None
    #　３．返回openid
    return data['openid']