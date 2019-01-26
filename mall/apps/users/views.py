from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from users.models import User
from users.serializers import RegisterUserSerializer, UserCenterInfoSerializer, UserEmailInfoSerializer, \
    AddUserBrowsingHistorySerializer, SKUSerializer, UserUpdatePasswordSerializer, UserResetPasswordSerializer
from users.serializers import AddressSerializer
from users.utils import check_token

"""
前段发送用户给后端，我们判断用户名是否　注册

"""
# APIView    基类
# GenericAPIView    对列表视图和详情视图做了通用支持，一般和mixin配合使用
# ListAPIView,RetrieveAPIView    封装好了

class RegisterUsernameCountAPIView(APIView):
    def get(self,request,username):
        count = User.objects.filter(username=username).count()
        # 组织数据
        context= {
            'count':count,
            'username':username
        }
        return Response(context)


class RegisterPhoneCountAPIView(APIView):
    """
    查询手机号的个数
    GET: /users/phones/(?P<mobile>1[345789]\d{9})/count/
    """
    def get(self,request,mobile):

        #通过模型查询获取手机号个数
        count = User.objects.filter(mobile=mobile).count()
        #组织数据
        context = {
            'count':count,
            'phone':mobile
        }

        return Response(context)


"""
1.接受数据
2.数据效验
3.数据入库
4.返回响应

POST  /users/register/
"""

class RegisterUserAPIView(APIView):
    def post(self,request):
        # 1.接受数据
        data=request.data
        # 2.数据效验
        serializer=RegisterUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3.数据入库
        serializer.save()

        # 4.返回响应
        # 序列化：将模型转换为JSON
        """
        如何序列化呢？
        我们的序列化器是根据字段来查询模型中对应数据，如果序列化器中有模型模型　中没有，则会报错
        如果再序列化器中设置write_only则会再序列化中忽略此字段
        """
        return Response(serializer.data)



    """
    当用户注册成功之后，自动登录
    自动登录的功能是要求用户注册成功之后，返回数据的时候需要添加额外一个token
    １．序列化的时候添加ｔｏｋｅｎ
    ２．token是怎么生成的
    """

"""
个人中心的信息展示　　必须是登录用户
１．让前端传递用户信息
２．我们根据用户信息来获取ｕｓｅｒ
３．将对象转化为字典数据
４．返回响应
GET  /users/infos/
"""
from rest_framework.permissions import IsAuthenticated
# class UserCenterInfoAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self,request):
#         # 1.获取用户信息
#         user = request.user
#         # 2.将模型转化为字典
#         serializer = UserCenterInfoSerializer(user)
#         #3.返回响应
#         return Response(serializer.data)
class UserCenterInfoAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserCenterInfoSerializer
    # 已有的父类不能满足我们的需求，需要重写
    def get_object(self):
        return self.request.user

"""
当用户 输入邮箱之后,点击保存的时候,
1.我们需要将 邮箱内容发送给后端,后端需要更新 指定用户的 email字段
2.同时后端需要给这个邮箱发送一个           激活连接
3.当用户点击激活连接的时候 ,改变 email_active的状态


用户 输入邮箱之后,点击保存的时候,
我们需要将 邮箱内容发送给后端

# 1. 后端需要接收 邮箱
# 2. 校验
# 3. 更新数据
# 4. 返回相应

PUT     /users/emails/

"""
#APIView                        基类
#GenericAPIVIew                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
#UpdateAPIView                   封装好了

# class UserEmailInfoAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#     def put(self,request):
#         # 1. 后端需要接收 邮箱
#         data = request.data
#         # 2. 校验                           更新某一个人的对象
#         serializer = UserEmailInfoSerializer(instance=request.user,data=data)
#         serializer.is_valid(raise_exception=True)
#         # 3. 更新数据
#         serializer.save()
#         # 4. 返回相应
#         return Response(serializer.data)
from rest_framework.generics import UpdateAPIView
class UserEmailInfoAPIView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserEmailInfoSerializer
    # 父类方法不能满足我们需求
    def get_object(self):
        return self.request.user

"""
激活需求:
当用户点击激活连接的时候,需要让前端接收到 token信息
然后让前端发送 一个请求,这个请求 包含  token信息

1. 接收token信息
2. 对token进行解析
3. 解析获取user_id之后,进行查询
4. 修改状态
5. 返回相应

GET     /users/emails/verification/
"""

class UserEmailVerificationAPIView(APIView):
    def get(self,request):
        # 1获取token信息
        token = request.query_params.get('token')
        if token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 2.对token进行解析
        user_id = check_token(token)
        if user_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # 3.解析获取user_id之后, 进行查询
        user = User.objects.get(pk=user_id)
        # 4.修改状态
        user.email_active = True
        user.save()
        # 5.返回相应
        return Response({'msg':'ok'})

"""
新增地址
    1.后端接受数据
    ２．对数据进行效验
    ３．数据入库
    ４．返回响应
POST  ／users/addresses/
"""
from rest_framework.generics import CreateAPIView
# class UserAddressesAPIView(CreateAPIView):
#     serializer_class = AddressSerializer
    # queery_set   新增数据用不到该数据


from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from users.serializers import AddressTitleSerializer

class AddressViewSet(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,GenericViewSet):
    """
    用户地址新增与修改
    list GET: /users/addresses/
    create POST: /users/addresses/
    destroy DELETE: /users/addresses/
    action PUT: /users/addresses/pk/status/
    action PUT: /users/addresses/pk/title/
    """

    #制定序列化器
    serializer_class = AddressSerializer
    #添加用户权限
    permission_classes = [IsAuthenticated]
    #由于用户的地址有存在删除的状态,所以我们需要对数据进行筛选
    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        """
        count = request.user.addresses.count()
        if count >= 20:
            return Response({'message':'保存地址数量已经达到上限'},status=status.HTTP_400_BAD_REQUEST)

        return super().create(request,*args,**kwargs)

    def list(self, request, *args, **kwargs):
        """
        获取用户地址列表
        """
        # 获取所有地址
        queryset = self.get_queryset()
        # 创建序列化器
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        # 响应
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': 20,
            'addresses': serializer.data,
        })

    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=True)
    def title(self, request, pk=None, address_id=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['put'], detail=True)
    def status(self, request, pk=None, address_id=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)





"""
添加浏览记录的业务逻辑
１．接受商品ｉｄ
２．效验数据
３．数据保存到数据库中
４．返回响应
post    /users/histories/
"""
class UserHistoryAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddUserBrowsingHistorySerializer

    """
    获取浏览历史记录　　GET
    """
    def get(self,request):
        user = request.user

        # 从redis中获取数据
        redis_conn = get_redis_connection('history')
        ids = redis_conn.lrange('history_%s'%user.id,0,4)
        # 根据id查询数据
        # skus = SKU.objects.filter(id_in=ids)  浏览顺序会变化
        skus = []
        for id in ids:
            sku = SKU.objects.get(pk=id)
            skus.append(sku)
        serializer = SKUSerializer(skus,many=True)
        return Response(serializer.data)





# 登录合并购物车　　　修改登录视图
from rest_framework_jwt.views import ObtainJSONWebToken
from carts.utils import merge_cookie_to_redis
class MergeLoginAPIView(ObtainJSONWebToken):


    def post(self, request, *args, **kwargs):
        # 调用jwt扩展的方法，对用户登录的数据进行验证
        response = super().post(request)

        # 如果用户登录成功，进行购物车数据合并
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # 表示用户登录成功
            user = serializer.validated_data.get("user")
            # 合并购物车
            # merge_cart_cookie_to_redis(request, user, response)
            response = merge_cookie_to_redis(request, user, response)


        return response


###################################用户修改密码视图########################################
class UserUpdatePasswordAPIView(APIView):
    """
    用户修改密码视图
    PUT  /users/user_id/password/
    """
    permission_classes = [IsAuthenticated]
    def put(self,request,user_id):
        # 获取用户信息
        user = User.objects.get(id=user_id)
        # 接收数据
        data = request.data
        # 校验数据
        serializer = UserUpdatePasswordSerializer(instance=user,data=data)
        serializer.is_valid(raise_exception=True)
        # 保存数据
        serializer.save()
        # 返回响应
        return Response({'message':'OK'},status=status.HTTP_200_OK)


#######################################重设密码视图######################################
class UserResetPasswordAPIView(APIView):
    """
    重设密码视图
    POST   /users/'+ this.user_id +'/passwords/
    """
    def post(self,request,user_id):
        data = request.data
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message':'用户不存在'})
        serializer = UserResetPasswordSerializer(data=data,instance=user)
        serializer.is_valid(raise_exception=True)
        # 保存密码
        serializer.save()
        # 返回响应
        return Response({'message':'OK'})