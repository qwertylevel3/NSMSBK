# coding:gbk
from django.shortcuts import render
from sqlModels.models import ServerGroupDat
from sqlModels.models import ServerList
from sqlModels.models import GroupList
from django.shortcuts import HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import time
import json
import logging


# log用，将数据库数据转化为字符串用来log
def serverGroup2Str(serverGroupData):
    serverGroupStr = ""
    serverGroupStr += "id:" + str(serverGroupData.id) + "|"
    serverGroupStr += "group_id:" + str(serverGroupData.group_id) + "|"
    serverGroupStr += "server_ids:" + serverGroupData.server_ids + "|"
    serverGroupStr += "time_out:" + str(serverGroupData.time_out)
    return serverGroupStr


# 记录服务器组修改操作
def logServerGroupRevise(request, groupid):
    serverGroup = ServerGroupDat.objects.get(group_id=groupid)
    logger = logging.getLogger("sql")
    logger.info("%s : revise server group [%s]",
                request.user.username,
                serverGroup2Str(serverGroup))


# 记录服务器组新增操作
def logServerGroupNew(request, groupid):
    serverGroup = ServerGroupDat.objects.get(group_id=groupid)
    logger = logging.getLogger("sql")
    logger.info("%s : create server group [%s]",
                request.user.username,
                serverGroup2Str(serverGroup))


# 根据服务器组id返回服务器组名称
def getServerGroupName(serverGroupID):
    allServerGroup = GroupList.objects.filter(id=serverGroupID)
    if len(allServerGroup) > 0:
        return allServerGroup[0].name
    return serverGroupID


# 将数据库记录转换为页面显示数据
def convert2ServerGroupResult(rawServerGroupData):
    serverGroupData = {}

    serverGroupData["id"] = rawServerGroupData.id
    serverGroupData["group_id"] = rawServerGroupData.group_id
    serverGroupData["server_ids"] = rawServerGroupData.server_ids
    serverGroupData["group_name"] = getServerGroupName(rawServerGroupData.group_id)

    return serverGroupData


# server序列化,用来传递json数据
def server2dict(server):
    return {
        'id': server.id,
        'ip': server.ip,
        'port': server.port,
        'idc': server.idc,
        'sign': server.sign,
        'is_used': server.is_used
    }


# 更改服务器组
#
# post:
# groupid
# groupName
# timeout
# serverList(服务器组关联所有server id组成的字符串)
#
# ret:
# result(是否操作成功)
@login_required
def ajHandleServerGroupRevise(request):
    id = request.POST.get("id", "-1")
    groupName = request.POST.get("groupName", "")
    timeout = request.POST.get("timeout", 6000)
    serverList = request.POST.get("serverList", "")

    updateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    registrationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    if id == "-1":
        # 查找改groupName是否存在
        if len(GroupList.objects.filter(name=groupName)) > 0:
            json_return = {
                "result": False
            }
            return JsonResponse(json_return)
        group = GroupList.objects.create(
            update_time=updateTime,
            registration_time=registrationTime,
            name=groupName
        )
        id = group.id
        groupData = ServerGroupDat.objects.create(
            group_id=id,
            update_time=updateTime,
            registration_time=registrationTime,
            server_ids=serverList,
            time_out=timeout
        )
        logServerGroupNew(request, id)
    else:
        # 如果是更改操作
        # 首先观察提交的groupName是否被改动
        # 如果被改动，检查改groupName是否已经存在
        # 否则直接修改
        oldGroup = ServerGroupDat.objects.get(id=id)
        oldGroupName = GroupList.objects.get(id=oldGroup.group_id).name

        if groupName != oldGroupName:
            if len(GroupList.objects.filter(name=groupName)) > 0:
                json_return = {
                    "result": False
                }
                return JsonResponse(json_return)

        oldGroup.update_time = updateTime
        oldGroup.server_ids = serverList
        oldGroup.time_out = timeout
        oldGroup.save()
        logServerGroupRevise(request, oldGroup.group_id)

        targetGroup = GroupList.objects.get(id=oldGroup.group_id)
        targetGroup.update_time = updateTime
        targetGroup.name = groupName
        targetGroup.save()

    json_return = {"result": True}
    return JsonResponse(json_return)


# 显示查询服务器组页面
#
# get:
#
# ret:
# result(所有服务器组信息)
@login_required
def serverGroupSearch(request):
    allServerGroup = ServerGroupDat.objects.all()
    # 显示所有服务器组
    result = []
    for serverGroup in allServerGroup:
        result.append(convert2ServerGroupResult(serverGroup))

    return render(request, "serverGroupConfig/serverGroupSearch.html",
                  {
                      "result": result
                  })


# 显示更改服务器组页面
#
# get:
# id(-1为新建服务器组，否则为更改服务器组)
#
# ret:
# id(同上)
# defaultServer(服务器组关联所有服务器id列表)
# allServer(所有服务器)
# allServerGroup(所有服务器组)
@login_required
def serverGroupRevise(request):
    defaultServer = []
    id = request.GET.get("id", "-1")
    groupName = ""

    # 如果get id不为-1，则为更改服务器组信息
    # 设置该服务器组默认参数
    if id != "-1":
        serverGroup = ServerGroupDat.objects.get(id=id)
        defaultServer = serverGroup.server_ids.split(',')
        groupName = GroupList.objects.get(id=serverGroup.group_id).name

    return render(request, "serverGroupConfig/serverGroupRevise.html",
                  {
                      "id": id,
                      "defaultServer": defaultServer,
                      "groupName": groupName,
                      "allServer": ServerList.objects.all(),
                      "allServerGroup": ServerGroupDat.objects.all()
                  })


# 显示某个服务器组详情
# 返回该服务器组关联的服务器列表
#
# get:
# id(查询的某个服务器组id)
#
# ret:
# result(id服务器组所关联所有服务器信息列表)
@login_required
def ajShowServerGroupDetail(request):
    id = request.GET.get("id", "-1")

    serverGroup = ServerGroupDat.objects.get(id=id)
    serveridList = serverGroup.server_ids.split(',')

    serverList = []
    for id in serveridList:
        server = ServerList.objects.filter(id=id)
        if len(server) > 0:
            serverList.append(server2dict(server[0]))

    return_json = {'result': serverList}
    return JsonResponse(return_json)


# 返回所有服务器信息，并根据id返回初始服务器id列表
#
# post:
# id(服务器组id)
#
# ret:
# serverList(所有服务器信息)
# defaultServerList(该服务器组关联所有服务器id列表)
@login_required
def ajInitServerGroupRevisePage(request):
    serverList = []

    id = request.POST.get("id", "-1")

    allServer = ServerList.objects.all()

    # 显示所有服务器
    for server in allServer:
        serverList.append(server2dict(server))

    # 如果id非-1，则为修改操作
    # 设置该服务器组关联所有服务器id
    defaultServerList = []
    if id != "-1":
        serverGroup = ServerGroupDat.objects.get(id=id)
        defaultServerList = serverGroup.server_ids.split(',')

    json_return = {
        "serverList": serverList,
        "defaultServerList": defaultServerList
    }
    return JsonResponse(json_return)
