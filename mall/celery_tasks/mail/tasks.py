from django.core.mail import send_mail
from celery_tasks.main import app

# name 就是设置名字
@app.task(name='哈哈')
def send_celery_email(subject,message,from_email,email, verify_url,recipient_list):
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)

    send_mail(subject=subject,
              message=message,
              from_email=from_email,
              recipient_list=recipient_list,
              html_message=html_message)