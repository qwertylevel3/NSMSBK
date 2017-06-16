from django.shortcuts import render
from sqlModels.models import ServerList
from django.shortcuts import HttpResponseRedirect
import time


def serverConfigDelete(request):
    id = request.POST.get("id", "-1")
    # 查找该项目是否存在
    targetData = ServerList.objects.filter(id=id)
    if len(targetData) > 0:
        for data in targetData:
            data.is_used = 0
            data.save()
    return HttpResponseRedirect('/serverConfigSearch/')


def handleServerRevise(request):
    if request.method != "POST":
        return serverConfigRevise(request)

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

    else:
        ServerList.objects.create(
            update_time=updateTime,
            registration_time=registrationTime,
            ip=ip,
            port=port,
            idc=idc,
            sign=sign,
            is_used=1
        )
    return HttpResponseRedirect('/serverConfigSearch/')


def serverConfigRevise(request):
    id = request.POST.get("id", "-1")

    return render(request, 'serverConfig/serverConfigRevise.html',
                  {"id": id,
                   "allServer": ServerList.objects.all()
                   })


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
                        sign == "" or server.sign == sign) and (
                    server.is_used == 1):
            result.append(server)

    return render(request, 'serverConfig/serverConfigSearch.html',
                  {
                      "result": result,
                  })
