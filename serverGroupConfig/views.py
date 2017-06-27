from django.shortcuts import render
from sqlModels.models import ServerGroupDat
from sqlModels.models import ServerList
from sqlModels.models import GroupList
from django.shortcuts import HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import time
import json


# Create your views here.

# 更改服务器组
@login_required
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


# 根据服务器组id返回服务器组名称
def getServerGroupName(serverGroupID):
    allServerGroup = GroupList.objects.filter(id=serverGroupID)
    if len(allServerGroup)>0:
        return allServerGroup[0].name
    return serverGroupID

# 将数据库记录转换为页面显示数据
def convert2ServerGroupResult(rawServerGroupData):
    serverGroupData={}

    serverGroupData["id"]=rawServerGroupData.id
    serverGroupData["group_id"]=rawServerGroupData.group_id
    serverGroupData["server_ids"]=rawServerGroupData.server_ids
    serverGroupData["group_name"]=getServerGroupName(rawServerGroupData.group_id)

    return serverGroupData


# 查询服务器组
@login_required
def serverGroupConfigSearch(request):
    allServerGroup = ServerGroupDat.objects.all()

    result=[]

    for serverGroup in allServerGroup:
        result.append(convert2ServerGroupResult(serverGroup))

    return render(request, "serverGroupConfig/serverGroupConfigSearch.html",
                  {
                      "result":result
                  })


# 显示更改服务器组页面
@login_required
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


# server序列化,用来传递json数据
def server2dict(server):
    return{
        'id':server.id,
        'ip':server.ip,
        'port':server.port,
        'idc':server.idc,
        'sign':server.sign
    }


# 显示某个服务器详情
@login_required
def showServerGroupDetail(request):
    id=request.GET.get("id","-1")

    serverGroup=ServerGroupDat.objects.get(id=id)
    serveridList=serverGroup.server_ids.split(',')

    serverList=[]
    for id in serveridList:
        server=ServerList.objects.filter(id=id)
        if len(server)>0:
            serverList.append(server2dict(server[0]))

    return_json = {'result': serverList }
    return JsonResponse(return_json)

