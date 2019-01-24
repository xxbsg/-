from django.contrib import admin
from . import models

# Register your models here.


# 为了让 admin 界面管理某个数据模型，我们需要先注册该数据模型到 admin
admin.site.register(models.ContentCategory)
admin.site.register(models.Content)
