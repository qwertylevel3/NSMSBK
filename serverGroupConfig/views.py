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


# log�ã������ݿ�����ת��Ϊ�ַ�������log
def serverGroup2Str(serverGroupData):
    serverGroupStr = ""
    serverGroupStr += "id:" + str(serverGroupData.id) + "|"
    serverGroupStr += "group_id:" + str(serverGroupData.group_id) + "|"
    serverGroupStr += "server_ids:" + serverGroupData.server_ids + "|"
    serverGroupStr += "time_out:" + str(serverGroupData.time_out)
    return serverGroupStr


# ��¼���������޸Ĳ���
def logServerGroupRevise(request, groupid):
    serverGroup = ServerGroupDat.objects.get(group_id=groupid)
    logger = logging.getLogger("sql")
    logger.info("%s : revise server group [%s]",
                request.user.username,
                serverGroup2Str(serverGroup))


# ��¼����������������
def logServerGroupNew(request, groupid):
    serverGroup = ServerGroupDat.objects.get(group_id=groupid)
    logger = logging.getLogger("sql")
    logger.info("%s : create server group [%s]",
                request.user.username,
                serverGroup2Str(serverGroup))


# ���ݷ�������id���ط�����������
def getServerGroupName(serverGroupID):
    allServerGroup = GroupList.objects.filter(id=serverGroupID)
    if len(allServerGroup) > 0:
        return allServerGroup[0].name
    return serverGroupID


# �����ݿ��¼ת��Ϊҳ����ʾ����
def convert2ServerGroupResult(rawServerGroupData):
    serverGroupData = {}

    serverGroupData["id"] = rawServerGroupData.id
    serverGroupData["group_id"] = rawServerGroupData.group_id
    serverGroupData["server_ids"] = rawServerGroupData.server_ids
    serverGroupData["group_name"] = getServerGroupName(rawServerGroupData.group_id)

    return serverGroupData


# server���л�,��������json����
def server2dict(server):
    return {
        'id': server.id,
        'ip': server.ip,
        'port': server.port,
        'idc': server.idc,
        'sign': server.sign,
        'is_used': server.is_used
    }


# ���ķ�������
#
# post:
# groupid
# groupName
# timeout
# serverList(���������������server id��ɵ��ַ���)
#
# ret:
# result(�Ƿ�����ɹ�)
@login_required
def ajHandleServerGroupRevise(request):
    id = request.POST.get("id", "-1")
    groupName = request.POST.get("groupName", "")
    timeout = request.POST.get("timeout", 6000)
    serverList = request.POST.get("serverList", "")

    updateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    registrationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    if id == "-1":
        # ���Ҹ�groupName�Ƿ����
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
        # ����Ǹ��Ĳ���
        # ���ȹ۲��ύ��groupName�Ƿ񱻸Ķ�
        # ������Ķ�������groupName�Ƿ��Ѿ�����
        # ����ֱ���޸�
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


# ��ʾ��ѯ��������ҳ��
#
# get:
#
# ret:
# result(���з���������Ϣ)
@login_required
def serverGroupSearch(request):
    allServerGroup = ServerGroupDat.objects.all()
    # ��ʾ���з�������
    result = []
    for serverGroup in allServerGroup:
        result.append(convert2ServerGroupResult(serverGroup))

    return render(request, "serverGroupConfig/serverGroupSearch.html",
                  {
                      "result": result
                  })


# ��ʾ���ķ�������ҳ��
#
# get:
# id(-1Ϊ�½��������飬����Ϊ���ķ�������)
#
# ret:
# id(ͬ��)
# defaultServer(��������������з�����id�б�)
# allServer(���з�����)
# allServerGroup(���з�������)
@login_required
def serverGroupRevise(request):
    defaultServer = []
    id = request.GET.get("id", "-1")
    groupName = ""

    # ���get id��Ϊ-1����Ϊ���ķ���������Ϣ
    # ���ø÷�������Ĭ�ϲ���
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


# ��ʾĳ��������������
# ���ظ÷�����������ķ������б�
#
# get:
# id(��ѯ��ĳ����������id)
#
# ret:
# result(id�����������������з�������Ϣ�б�)
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


# �������з�������Ϣ��������id���س�ʼ������id�б�
#
# post:
# id(��������id)
#
# ret:
# serverList(���з�������Ϣ)
# defaultServerList(�÷�������������з�����id�б�)
@login_required
def ajInitServerGroupRevisePage(request):
    serverList = []

    id = request.POST.get("id", "-1")

    allServer = ServerList.objects.all()

    # ��ʾ���з�����
    for server in allServer:
        serverList.append(server2dict(server))

    # ���id��-1����Ϊ�޸Ĳ���
    # ���ø÷�������������з�����id
    defaultServerList = []
    if id != "-1":
        serverGroup = ServerGroupDat.objects.get(id=id)
        defaultServerList = serverGroup.server_ids.split(',')

    json_return = {
        "serverList": serverList,
        "defaultServerList": defaultServerList
    }
    return JsonResponse(json_return)
