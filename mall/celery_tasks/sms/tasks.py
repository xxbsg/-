# 任务就是普通的函数
# １．普通的函数必须要被celery实例对象的task装饰器装饰
# ２．这个人物需要celery自己去检测
from libs.yuntongxun.sms import CCP
from celery_tasks.main import app

@app.task
def send_sms_code(mobile,sms_code):
    CCP().send_template_sms(mobile,[sms_code,5],1)