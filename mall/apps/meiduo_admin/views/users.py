from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from meiduo_admin.serializer.users import AdminLoginSerializer, AdminUserSerializer
from users.models import User


class AdminLoginAPIView(APIView):
    """
    后台登录视图
    POST /meiduo_admin/authorizations/
    """


    def post(self,request):
        # 接收数据
        data = request.data
        # 校验数据
        serializer = AdminLoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 生成token
        user = serializer.validated_data.get('user')
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        # 反回响应
        return Response({'id':user.id,
                         'username':user.username,
                         'token':token})


class AdminUserAPIView(APIView):
    """
    后台用户管理视图 查询
    GET /meiduo_admin/users/?keyword=<搜索内容>&page=<页码>&pagesize=<页容量>
    """
    def get(self,request):
        params = request.query_params
        if params['keyword'] is "":
            users = User.objects.all()
            counts = len(users)
            # 遍历用户列表
            user_list = []
            for user in users:
                user_list.append({
                    'id':user.id,
                    'username':user.username,
                    'mobile':user.mobile,
                    'email':user.email
                })
            page = params.get('page')
            pagesize = params.get('pagesize')
            remainder = int(counts) % int(pagesize)
            pages = int(counts) // int(pagesize)
            if remainder != 0:
                pages += 1
            # 返回响应  0-9 10-19 20-29
            a = (int(page)-1)*10
            user_lists=user_list[a:a+10]
            return Response({"counts":counts,
                             "list":user_lists,
                             "page":int(page),
                             "pages":pages,
                             "pagesize":int(pagesize)})
        else:
            users = User.objects.all()
            keyword = params.get('keyword')
            user_list=[]
            for user in users:
                if keyword in str(user.id) or keyword in str(user.username) or keyword in str(user.email) or keyword in str(user.mobile):
                    user_list.append({
                        'id': user.id,
                        'username': user.username,
                        'mobile': user.mobile,
                        'email': user.email
                    })
            counts= len(user_list)
            page = params.get('page')
            pagesize = params.get('pagesize')
            remainder = int(counts) % int(pagesize)
            pages = int(counts) // int(pagesize)
            if remainder != 0:
                pages += 1
            # 返回响应
            return Response({"counts": counts,
                             "list": user_list,
                             "page": int(page),
                             "pages": pages,
                             "pagesize": int(pagesize)})


    def post(self,request):
        """
        后台用户新增视图
        POST  /meiduo_admin/users/
        """
        # 接收数据
        data = request.data
        username = request.data.get('username')
        # 校验数据
        serializer = AdminUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 保存数据
        serializer.save()
        # 返回响应
        user = User.objects.get(username=username)
        return Response({"id":user.id,
                         "username":user.username,
                         "mobile":user.mobile,
                         "email":user.email},status=201)


# 商品sku管理视图