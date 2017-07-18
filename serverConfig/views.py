# coding:gbk
from django.shortcuts import render
from sqlModels.models import ServerList
from django.shortcuts import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required
import json
import time
import logging


# ���ݿ�����ת��Ϊ�ַ���������log
def serverData2Str(serverData):
    serverStr = ""
    serverStr += "id:" + str(serverData.id) + "|"
    serverStr += "ip:" + serverData.ip + "|"
    serverStr += "port:" + serverData.port + "|"
    serverStr += "idc:" + serverData.idc + "|"
    serverStr += "sign:" + serverData.sign
    return serverStr


# log����������
def logServerRevise(request, id):
    server = ServerList.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : revise server [%s]",
                request.user.username,
                serverData2Str(server))


# log����������
def logServerNew(request, id):
    server = ServerList.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : create server [%s]",
                request.user.username,
                serverData2Str(server))


# log����������
def logServerReuse(request, id):
    server = ServerList.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : reuse server [%s]",
                request.user.username,
                serverData2Str(server))


# log����������
def logServerDelete(request, id):
    server = ServerList.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : delete server [%s]",
                request.user.username,
                serverData2Str(server))


# �������б����л�
def serverList2dict(serverList):
    result = []
    for server in serverList:
        result.append(
            {
                "id": server.id,
                "ip": server.ip,
                "port": server.port,
                "idc": server.idc,
                "sign": server.sign,
                "is_used": server.is_used
            }
        )
    return result


# ɾ��һ����������Ŀ��is_used����Ϊ0��
#
# post:
# id(������id)
#
# ret:
# result(�����ɹ�)
@login_required
def ajServerDelete(request):
    id = request.POST.get("id", "-1")
    targetData = ServerList.objects.get(id=id)
    targetData.is_used = 0
    targetData.save()
    logServerDelete(request, targetData.id)
    json_return = {"result": True}
    return JsonResponse(json_return)


# ����һ����������Ŀ��is_used����Ϊ1��
#
# post:
# id(������id)
#
# ret:
# result(�����ɹ�)
@login_required
def ajServerReuse(request):
    id = request.POST.get("id", "-1")
    targetData = ServerList.objects.get(id=id)
    targetData.is_used = 1
    targetData.save()
    logServerReuse(request, targetData.id)
    json_return = {"result": True}
    return JsonResponse(json_return)


# ����ip��port�Ƿ��Ѵ���
def validateServer(ip, port):
    dupData = ServerList.objects.filter(ip=ip, port=port)
    if len(dupData) > 0:
        return False
    return True




def ajValidateServer(request):
    ip=request.POST.get("ip",-1)
    port=request.POST.get("port",-1)

    if validateServer(ip,port):
        json_return={
            "result":True
        }
        return JsonResponse(json_return)
    json_return={
        "result":False
    }
    return JsonResponse(json_return)


# �������߸�����Ŀ
#
# post:
# id(�޸ĵ���Ŀ��id)
# ip
# port
# idc
# sign
#
# ret:
# result(True:�����ɹ� | False:����ʧ��)
# msg(������Ϣ)
@login_required
def ajHandleServerRevise(request):
    id = request.POST.get("id", "-1")
    ip = request.POST.get("ip", "")
    port = request.POST.get("port", "")
    idc = request.POST.get("idc", "")
    sign = request.POST.get("sign", "")

    updateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    registrationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


    # ����
    # ���ȼ���Ƿ������ip��port
    # ��������ˣ�����
    targetData = ServerList.objects.get(id=id)
    if targetData.ip != ip or targetData.port != port:
        if not validateServer(ip, port):
            return_json = {
                'result': False
            }
            return JsonResponse(return_json)
    targetData.ip = ip
    targetData.port = port
    targetData.idc = idc
    targetData.sign = sign
    targetData.update_time = updateTime
    targetData.save()
    logServerRevise(request, targetData.id)

    return_json = {
        'result': True
    }
    return JsonResponse(return_json)


def ajHandleServerAdd(request):
    ip = request.POST.get("ip", "")
    port = request.POST.get("port", "")
    idc = request.POST.get("idc", "")
    sign = request.POST.get("sign", "")

    updateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    registrationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    # ����
    # ����
    if not validateServer(ip, port):
        return_json = {
            'result': False
        }
        return JsonResponse(return_json)

    data = ServerList.objects.create(
        update_time=updateTime,
        registration_time=registrationTime,
        ip=ip,
        port=port,
        idc=idc,
        sign=sign,
        is_used=1
    )
    logServerNew(request, data.id)
    json_return = {
        'result': True
    }
    return JsonResponse(json_return)


# ��ʾ���ķ�������Ϣ������
#
# get:
# id(��Ҫ����ķ�����id��-1Ϊ��������Ҫ����ҳ������Ĭ�ϲ���)
#
# ret:
# id(ͬ��)
# allServer
@login_required
def serverRevise(request):
    id = request.GET.get("id", "-1")

    return render(request, 'serverConfig/serverRevise.html',
                  {"id": id,
                   "allServer": ServerList.objects.all()
                   })


# ��ʾ������������ҳ��
#
# get:
#
# ret:
@login_required
def serverSearch(request):
    return render(request, 'serverConfig/serverSearch.html')


# ����������
#
# get:
# ip
# port
# idc
# sign
#
# ret:
# result(������������Ϣ�б�)
# resultSize(�б���)
@login_required
def ajServerSearch(request):
    result = []

    ip = request.POST.get("ip", "")
    port = request.POST.get("port", "")
    idc = request.POST.get("idc", "")
    sign = request.POST.get("sign", "")

    allServer = ServerList.objects.all()

    for server in allServer:
        if (ip == "" or server.ip == ip) and (
                        port == "" or server.port == port) and (
                        idc == "" or server.idc == idc) and (
                        sign == "" or server.sign == sign):
            result.append(server)

    resultSize = len(result)

    json_return = {"result": serverList2dict(result), "resultSize": resultSize}
    return JsonResponse(json_return)
