from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from apps.user.models import User
from django.views.generic import View
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, HttpRequest
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from celery_tasks.tasks import send_register_active_email
import re


# Create your views here.
# def register(request):
#     if request.method == 'GET':
#         '''用户注册界面'''
#         return render(request, 'register.html')
#     elif request.method == 'POST':
#         username = request.POST.get('user_name')
#         password = request.POST.get('pwd')
#         email = request.POST.get('email')
#         allow = request.POST.get('allow')
#
#         if not all([username, password, email]):
#             return render(request, 'register.html', {'errmsg': '数据不完整'})
#
#         if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
#             return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
#
#         if allow != 'on':
#             return render(request, 'register.html', {'errmsg': '请同意协议'})
#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             user = None
#
#         if user:
#             return render(request, 'register.html', {'errmsg': '用户名已存在'})
#
#         # 进行业务处理:进行用户注册
#         user = User.objects.create_user(username, email, password)
#         user.is_active = 0
#         user.save()
#
#         return redirect(reverse('goods:index'))


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user:
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 进行业务处理:进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 加载用户的身份信息，生成激活token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'comfirm': user.id}
        token = serializer.dumps(info)
        token = token.decode()

        # 发邮件
        send_register_active_email.delay(email, username, token)
        return redirect(reverse('goods:index'))


class ActiveView(View):
    '''用户激活'''

    def get(self, request, token):
        '''进行用户激活'''
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            user_id = info['confirm']

            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            return redirect(reverse('user:login'))

        except SignatureExpired as e:
            return HttpResponse('激活链接已过期')


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

# def register_handle(request):
#     '''进行注册处理'''
#     username = request.POST.get('user_name')
#     password = request.POST.get('pwd')
#     email = request.POST.get('email')
#     allow = request.POST.get('allow')
#
#     if not all([username, password, email]):
#         return render(request, 'register.html', {'errmsg': '数据不完整'})
#
#     if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
#         return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
#
#     if allow != 'on':
#         return render(request, 'register.html', {'errmsg': '请同意协议'})
#     try:
#         user = User.objects.get(username=username)
#     except User.DoesNotExist:
#         user = None
#
#     if user:
#         return render(request, 'register.html', {'errmsg': '用户名已存在'})
#
#     # 进行业务处理:进行用户注册
#     user = User.objects.create_user(username, email, password)
#     user.is_active = 0
#     user.save()
#
#     return redirect(reverse('goods:index'))
