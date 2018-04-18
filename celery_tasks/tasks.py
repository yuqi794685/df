from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "df.settings")
django.setup()

#创建一个celery类的实例对象
app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/8')

#定义任务函数
@app.task
def send_register_active_email(email, username, token):
    '''发送激活邮件'''
    #组织邮件信息
    subject = '天天生鲜欢迎您'
    message = '邮件正文'
    from_email = settings.EMAIL_FROM
    reciver = [email]
    html_message = '<h1>%s, 欢迎来到天天生鲜.</h1>请点击下面的链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (
        username, token, token)
    send_mail(subject, message, from_email, reciver, html_message=html_message)