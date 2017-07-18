# coding:gbk
from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import render_to_response


# Create your views here.


# 显示登录主界面
def auth(request):
    return render(request, 'auth/login.html')


# 检查是否登录成功
def check(request):
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")

    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return_json = {'result': True}
        return JsonResponse(return_json)
    else:
        return_json = {'result': False}
        return JsonResponse(return_json)
