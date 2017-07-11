from django.shortcuts import render
from sqlModels.models import ServerList
from django.shortcuts import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required
import json
import time
import logging


# 数据库数据转换为字符串，用来log
def serverData2Str(serverData):
    serverStr = ""
    serverStr += "id:" + str(serverData.id) + "|"
    serverStr += "ip:" + serverData.ip + "|"
    serverStr += "port:" + serverData.port + "|"
    serverStr += "idc:" + serverData.idc + "|"
    serverStr += "sign:" + serverData.sign
    return serverStr


# log服务器更改
def logServerRevise(request, id):
    server = ServerList.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : revise server [%s]",
                request.user.username,
                serverData2Str(server))


# log服务器新增
def logServerNew(request, id):
    server = ServerList.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : create server [%s]",
                request.user.username,
                serverData2Str(server))


# log服务器启用
def logServerReuse(request, id):
    server = ServerList.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : reuse server [%s]",
                request.user.username,
                serverData2Str(server))


# log服务器禁用
def logServerDelete(request, id):
    server = ServerList.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : delete server [%s]",
                request.user.username,
                serverData2Str(server))


# 服务器列表序列化
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


# 删除一个服务器条目（is_used设置为0）
#
# post:
# id(服务器id)
#
# ret:
# result(操作成功)
@login_required
def ajServerDelete(request):
    id = request.POST.get("id", "-1")
    targetData = ServerList.objects.get(id=id)
    targetData.is_used = 0
    targetData.save()
    logServerDelete(request, targetData.id)
    json_return = {"result": True}
    return JsonResponse(json_return)


# 启用一个服务器条目（is_used设置为1）
#
# post:
# id(服务器id)
#
# ret:
# result(操作成功)
@login_required
def ajServerReuse(request):
    id = request.POST.get("id", "-1")
    targetData = ServerList.objects.get(id=id)
    targetData.is_used = 1
    targetData.save()
    logServerReuse(request, targetData.id)
    json_return = {"result": True}
    return JsonResponse(json_return)


# 新增或者更改条目
#
# post:
# id(-1为新增，否则为修改)
# ip
# port
# idc
# sign
#
# ret:
# result(True:操作成功 | False:插入重复数据)
@login_required
def ajHandleServerRevise(request):
    id = request.POST.get("id", "-1")
    ip = request.POST.get("ip", "")
    port = request.POST.get("port", "")
    idc = request.POST.get("idc", "")
    sign = request.POST.get("sign", "")

    updateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    registrationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

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
        # 如果是新增，观察是否重复
        dupData = ServerList.objects.filter(ip=ip, port=port, idc=idc, sign=sign)
        if len(dupData) > 0:
            return_json = {'result': False}
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
    return_json = {'result': True}
    return JsonResponse(return_json)


# 显示更改服务器信息主界面
#
# get:
# id(需要处理的服务器id，-1为新增，主要用来页面设置默认参数)
#
# ret:
# id(同上)
# allServer
@login_required
def serverRevise(request):
    id = request.GET.get("id", "-1")

    return render(request, 'serverConfig/serverRevise.html',
                  {"id": id,
                   "allServer": ServerList.objects.all()
                   })


# 显示搜索服务器主页面
#
# get:
#
# ret:
@login_required
def serverSearch(request):
    return render(request, 'serverConfig/serverSearch.html')


# 搜索服务器
#
# get:
# ip
# port
# idc
# sign
#
# ret:
# result(搜索服务器信息列表)
# resultSize(列表长度)
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
