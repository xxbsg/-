from django.db import models

# Create your models here.

from django.db import models
class Area(models.Model):
    name = models.CharField(max_length=20,verbose_name='名称')
    parent = models.ForeignKey('self',on_delete=models.SET_NULL,null=True,blank=True,related_name = 'subs',verbose_name='上级行政区划')
    # related_name = 'subs',  related_name 关联对象反向引用描述符
    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = '行政区划'

    def __str__(self):   # 返回一个对象的描述信息
        return self.name