
from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.utils.deconstruct import deconstructible

# 4. 您的存储类必须是可解构的， 以便在迁移中的字段上使用它时可以对其进行序列化。
# 只要您的字段具有可自行序列化的参数，
# 就 可以使用 django.utils.deconstruct.deconstructible类装饰器
from mall import settings


@deconstructible

# 1.您的自定义存储系统必须是以下子类 django.core.files.storage.Storage：
class MyStorage(Storage):

# 2.Django必须能够在没有任何参数的情况下实例化您的存储系统。
# 这意味着任何设置都应该来自django.conf.settings：

    def __init__(self,config_path=None,config_url=None):
        if not config_path:
            fdfs_config = settings.FDFS_CLIENT_CONF
            self.fdfs_config = fdfs_config
        if not config_url:
            fdfs_url = settings.FDFS_URL
            self.fdfs_url = fdfs_url

    # 3.您的存储类必须实现_open()和_save() 方法以及适用于您的存储类的任何其他方法
        # open　打开　　因为我们的 Fdfs 是通过http来获取图片的,所以不需要打开方法
    def _open(self, name, mode='rb'):
        pass
        # save　保存
    def _save(self, name, content, max_length=None):
        # name,              文件的名字 我们不能通过名字 获取文件的完整路径
        # content,          content 内容 就是上传的内容 二进制

# １．创建Fdfs的客户端，让客户端加载配置文件
        # client = Fdfs_client('utils/fastdfs/client.conf')
        # client = Fdfs_client(settings.FDFS_CLIENT_CONF)
        client = Fdfs_client(self.fdfs_config)

# ２．获取上传的文件内容
            # 读取content内容；读取的是二进制
        file_data = content.read()
# ３．上传图片，并获取返回内容
        # upload_by_buffer 上传二进制图片
        result = client.upload_by_buffer(file_data)
# ４．根据返回内容获取remote  file_id
        """
        {'Storage IP': '192.168.35.83',
        'Group name': 'group1',
        'Remote file_id': 'group1/M00/00/00/wKgjU1w9i02AK-paAAN_pTILmEg459.jpg',
        'Local file name': '/home/python/Desktop/1.jpg',
        'Uploaded size': '223.00KB',
        'Status': 'Upload successed.'}
        """

        if result.get('Status') == 'Upload successed.':
            # 说明上传成功
            file_id = result.get('Remote file_id')
        else:
            raise Exception('上传失败')
        # 返回file_id
        return file_id

    # exists  存在　　Ｆdfs做了重名的处理　我们只需要上传就可以
    def exists(self, name):
        return False


    def url(self, name):
        # 默认调用 storage的 url方法 会返回 name(file_id)
        # http://192.168.35.83:8888/group1/M00/00/00/wKgjU1w9i02AK-paAAN_pTILmEg459.jpg
        # 实际我们访问图片的时候 是通过 http://ip:port/ + name(file_id)

        # return 'http://192.168.35.57:8888/'+name
        # return settings.FDFS_URL+name
        return self.fdfs_url + name