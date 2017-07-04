from django.shortcuts import render
from sqlModels.models import ServerList
from django.shortcuts import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required
import json
import time
import logging


def serverData2Str(serverData):
    serverStr = ""
    serverStr += "id:" + str(serverData.id) + "|"
    serverStr += "ip:" + serverData.ip + "|"
    serverStr += "port:" + serverData.port + "|"
    serverStr += "idc:" + serverData.idc + "|"
    serverStr += "sign:" + serverData.sign
    return serverStr


def logServerRevise(request, id):
    server=ServerList.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : revise server %s[%s]",
                request.user.username,
                id,
                serverData2Str(server))


def logServerNew(request, id):
    server=ServerList.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : create server %s[%s]",
                request.user.username,
                id,
                serverData2Str(server))


def logServerReuse(request,id):
    server=ServerList.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : reuse server %s[%s]",
                request.user.username,
                id,
                serverData2Str(server))

def logServerDelete(request, id):
    server=ServerList.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : delete server %s[%s]",
                request.user.username,
                id,
                serverData2Str(server))


# 删除一个服务器条目（is_used设置为0）
@login_required
def serverConfigDelete(request):
    id = request.POST.get("id", "-1")
    # 查找该项目是否存在
    targetData = ServerList.objects.filter(id=id)
    if len(targetData) > 0:
        for data in targetData:
            data.is_used = 0
            data.save()
            logServerDelete(request, data.id)
            json_return={"result":True}
            return JsonResponse(json_return)
    json_return={"result":False}
    return JsonResponse(json_return)

# 启用一个服务器条目（is_used设置为1）
@login_required
def serverConfigReuse(request):
    id = request.POST.get("id", "-1")
    # 查找该项目是否存在
    targetData = ServerList.objects.filter(id=id)
    if len(targetData) > 0:
        for data in targetData:
            data.is_used = 1
            data.save()
            logServerReuse(request, data.id)
            json_return={"result":True}
            return JsonResponse(json_return)
    json_return={"result":False}
    return JsonResponse(json_return)

# 新增或者更改条目
# 表单中id为-1为新增，否则为更改
@login_required
def handleServerRevise(request):
    ip = request.POST.get("ip", "")
    port = request.POST.get("port", "")
    idc = request.POST.get("idc", "")
    sign = request.POST.get("sign", "")

    updateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    registrationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    id = request.POST.get("id", "-1")
    # 查找该项目是否存在
    targetData = ServerList.objects.filter(id=id)

    if len(targetData) > 0:
        for data in targetData:
            data.ip = ip
            data.port = port
            data.idc = idc
            data.sign = sign
            data.update_time = updateTime
            data.save()
            logServerRevise(request, data.id)

    else:
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


# 显示更改服务器信息主界面
@login_required
def serverConfigRevise(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        ip = request.POST.get('ip')
        port = request.POST.get('port')
        idc = request.POST.get('idc')
        sign = request.POST.get('sign')

        targetData = ServerList.objects.filter(ip=ip, port=port, idc=idc, sign=sign)

        if len(targetData) > 0:
            return_json = {'result': False}
            return JsonResponse(return_json)
        else:
            handleServerRevise(request)
            return_json = {'result': True}
            return JsonResponse(return_json)
    else:
        id = request.GET.get("id", "-1")

        return render(request, 'serverConfig/serverConfigRevise.html',
                      {"id": id,
                       "allServer": ServerList.objects.all()
                       })


def serverList2dict(serverList):
    result=[]
    for server in serverList:
        result.append(
            {
                "id":server.id,
                "ip":server.ip,
                "port":server.port,
                "idc":server.idc,
                "sign":server.sign,
                "is_used":server.is_used
            }
        )
    return result


# 显示搜索服务器主界面
@login_required
def serverConfigSearch(request):
    result = []
    ip = ""
    port = ""
    idc = ""
    sign = ""

    if request.method == "POST":
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

    if request.method=="POST":
        json_return={"result": serverList2dict(result),"resultSize":resultSize}
        return JsonResponse(json_return)

    return render(request, 'serverConfig/serverConfigSearch.html',
                  {
                      "result": result,
                      "resultSize": resultSize
                  })
