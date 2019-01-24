from celery import Celery
"""
1.创建任务
2.创建Celery实例
3.再celery中设置任务，broker
4.worker执行人物
"""
# 第一种方式
# import os
# os.environ.setdefault('DJANGO_SETTINGS_MODULE','mall.settings')

# 第二种方式：
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE']='mall.settings'

# 2.创建celery实例
# main习惯添加celery的文件路径,确保main不出现重复
app = Celery(main='celery_tasks')

#3.设置broker
# 加载broker的配置信息：　　参数：路径信息
app.config_from_object('celery_tasks.config')

# 4.让celery自动检测任务
# 参数：列表　　　元素：任务的包路径
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.mail','celery_tasks.html'])

# 5.让worker去执行人物
# 需要再虚拟环境中执行命令
# celery -A celery实例对象的文件路径 worker -l info
# celery -A celery_tasks.main worker -l info