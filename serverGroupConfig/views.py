from django.shortcuts import render
from sqlModels.models import ServerGroupDat
from sqlModels.models import ServerList
from django.shortcuts import HttpResponseRedirect
import time


# Create your views here.

def handleServerGroupRevise(request):
    serverIdList = []

    for server in ServerList.objects.all():
        if request.POST.get("checkbox" + str(server.id), "") == "on":
            serverIdList.append(server.id)

    serverListStr = ""

    for serverid in serverIdList:
        serverListStr += "," + str(serverid)

    if serverListStr != "":
        serverListStr = serverListStr[1:]

    updateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    registrationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    id = int(request.POST.get("id", "-1"))
    # 查找该项目是否存在
    targetData = ServerGroupDat.objects.filter(id=id)

    timeout = request.POST.get("timeout", 6000)

    groupid=int(request.POST.get("groupid",99))

    if len(targetData) > 0:
        for data in targetData:
            data.group_id=groupid
            data.update_time = updateTime
            data.server_ids = serverListStr
            data.time_out = timeout
            data.save()
    else:
        ServerGroupDat.objects.create(
            group_id=groupid,
            update_time=updateTime,
            registration_time=registrationTime,
            server_ids=serverListStr,
            time_out=timeout
        )
    return HttpResponseRedirect('/serverGroupConfigSearch/')


def serverGroupConfigSearch(request):
    allServerGroup = ServerGroupDat.objects.all()

    return render(request, "serverGroupConfig/serverGroupConfigSearch.html",
                  {
                      "allServerGroup": allServerGroup
                  })


def serverGroupConfigRevise(request):
    defaultServer = []
    id = request.GET.get("id", "-1")

    if id != "-1":
        serverGroup = ServerGroupDat.objects.get(id=id)
        defaultServer = serverGroup.server_ids.split(',')

    return render(request, "serverGroupConfig/serverGroupConfigRevise.html",
                  {
                      "id": id,
                      "defaultServer": defaultServer,
                      "allServer": ServerList.objects.all(),
                      "allServerGroup": ServerGroupDat.objects.all()
                  })
