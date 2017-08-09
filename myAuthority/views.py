# coding:gbk
from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.utils.crypto import pbkdf2
from django.contrib.auth.hashers import make_password
from myAuthority.myDecorators import super_required
import time


# Create your views here.


# ��ʾ��¼������
def auth(request):
    return render(request, 'auth/login.html')


# ����Ƿ��¼�ɹ�
#
# post:
# username
# password
#
# ret:
# result(�Ƿ��¼�ɹ�)
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


# ���߼�����Ա�Ƿ��¼�ɹ�
#
# post:
# username
# password
#
# ret:
# result(�Ƿ��¼�ɹ�)
def checkSuper(request):
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")

    user=None
    userList=User.objects.filter(username=username)
    if len(userList)>0:
        if userList[0].is_superuser:
            user = authenticate(username=username, password=password)

    if user is not None:
        login(request, user)
        return_json = {'result': True}
        return JsonResponse(return_json)
    else:
        return_json = {'result': False}
        return JsonResponse(return_json)

# ��ѯ���е��û�
#
# get/post
#
# ret:
# userList(�����û��б�)
@super_required
def ajQueryAllUser(request):
    allUser = User.objects.all()

    result = []
    for user in allUser:
        result.append(
            {
                "id": user.id,
                "name": user.username
            }
        )
    return JsonResponse(
        {
            "userList": result
        }
    )


# ��ʾ�����û�����
@super_required
def managerUser(request):
    allUser = User.objects.all()

    return render(request, 'auth/managerUser.html',
                  {
                      "allUser": allUser
                  })

# ��ʾ�����û�����
@super_required
def addUser(request):
    return render(request, "auth/addUser.html")


# �����û�
#
# post:
# name
# pw
# isSuper(onΪ��������Ա��offΪ��ͨ�û�)
#
# ret:
# result(�����Ƿ�ɹ�)
@super_required
def ajHandleAddUser(request):
    name = request.POST.get("name", "")
    pw = make_password(request.POST.get("pw", ""))

    isSuper=False
    if request.POST.get("isSuper","off")=="on":
        isSuper=True

    registrationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    user = User.objects.create(
        username=name,
        password=pw,
        date_joined=registrationTime,
        is_superuser=isSuper
    )

    return JsonResponse(
        {
            "result": True
        }
    )

# ��ʾ�����û�ҳ��
#
# get:
# id(Ҫ���ĵ��û�id)
@super_required
def reviseUser(request):
    id = request.GET.get("id", "")

    user = User.objects.get(id=id)

    name = user.username
    isSuper="False"
    if user.is_superuser:
        isSuper="True"



    return render(request, "auth/reviseUser.html",
                  {
                      "id": id,
                      "name": name,
                      "isSuper":isSuper
                  })

# �����û���Ϣ
#
# post:
# id
# name
# pw
# isSuper
#
# ret:
# result(�Ƿ���ĳɹ�)
@super_required
def ajHandleReviseUser(request):
    id = request.POST.get("id", "")
    name = request.POST.get("name", "")
    pw = make_password(request.POST.get("pw", ""))
    isSuper=False
    if request.POST.get("isSuper","off")=="on":
        isSuper=True

    user = User.objects.get(id=id)

    user.username = name
    user.password = pw
    user.is_superuser=isSuper
    user.save()

    return JsonResponse(
        {
            "result": True
        }
    )

# ��ѯĳ���û����Ƿ����
#
# get:
# name
#
# ret:
# result
@super_required
def ajQueryUser(request):
    name = request.GET.get("name", "")

    userlist = User.objects.filter(username=name)

    if len(userlist) > 0:
        return JsonResponse({
            "result": False
        })

    return JsonResponse({
        "result": True
    })

