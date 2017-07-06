from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from sqlModels.models import ServerRuleDat
from sqlModels.models import CountryList
from sqlModels.models import CityList
from sqlModels.models import ProvList
from sqlModels.models import NetList
from sqlModels.models import ServerGroupDat
from sqlModels.models import GroupList
import time
import logging
from ruleConfig.ruleCondition import RuleCondition


# 数据库rule信息转化为字符串，用来log
def ruleData2Str(ruleData):
    ruleStr = ""
    ruleStr += "id:" + str(ruleData.id) + "|"
    ruleStr += "group_id:" + str(ruleData.group_id) + "|"
    ruleStr += "rule:" + ruleData.rule + "|"
    ruleStr += "rank:" + str(ruleData.rank) + "|"
    ruleStr += "ttl:" + str(ruleData.ttl) + "|"
    ruleStr += "compel:" + str(ruleData.compel)
    return ruleStr


# log规则更改
def logRuleRevise(request, id):
    rule = ServerRuleDat.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : revise rule %s[%s]",
                request.user.username,
                id,
                ruleData2Str(rule))


# log规则新增
def logRuleNew(request, id):
    rule = ServerRuleDat.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : create rule %s[%s]",
                request.user.username,
                id,
                ruleData2Str(rule))


# log规则启用
def logRuleReuse(request, id):
    rule = ServerRuleDat.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : reuse rule %s[%s]",
                request.user.username,
                id,
                ruleData2Str(rule))


# log规则禁用
def logRuleDelete(request, id):
    rule = ServerRuleDat.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : delete rule %s[%s]",
                request.user.username,
                id,
                ruleData2Str(rule))


# 根据国家代码返回国家名称
def getCountryName(countryID):
    if len(countryID) > 0:
        country = CountryList.objects.get(code=int(countryID))
        return country.name
    return ""


# 根据省份代码返回省份名称
def getProvinceName(provinceID):
    if len(provinceID) > 0:
        province = ProvList.objects.get(code=int(provinceID))
        return province.name
    return ""


# 根据城市代码返回城市名称
def getCityName(cityID):
    if len(cityID) > 0:
        city = CityList.objects.get(code=int(cityID))
        return city.name
    return ""


# 根据服务器组id返回服务器组名称
def getServerGroupName(serverGroupID):
    allServerGroup = GroupList.objects.filter(id=serverGroupID)
    if len(allServerGroup) > 0:
        return allServerGroup[0].name
    return serverGroupID


# 根据网络代码返回网络名称
def getNetName(netCode):
    if len(netCode) > 0:
        net = NetList.objects.filter(code=netCode)
        if len(net) > 0:
            return net[0].name
    return netCode


# 将数据库数据转换为在search页面显示的数据项
def convert2SearchResult(rawResultData):
    resultData = {}
    ruleCondition = RuleCondition(rawResultData.rule)

    resultData["id"] = rawResultData.id
    resultData["group_id"] = getServerGroupName(rawResultData.group_id)
    resultData["rank"] = rawResultData.rank
    resultData["ttl"] = rawResultData.ttl
    resultData["compel"] = rawResultData.compel

    if ruleCondition.countryInvert == 1:
        resultData["country"] = "!=" + getCountryName(ruleCondition.country)
    else:
        resultData["country"] = getCountryName(ruleCondition.country)

    if ruleCondition.provinceInvert == 1:
        resultData["province"] = "!=" + getProvinceName(ruleCondition.province)
    else:
        resultData["province"] = getProvinceName(ruleCondition.province)

    if ruleCondition.cityInvert == 1:
        resultData["city"] = "!=" + getCityName(ruleCondition.city)
    else:
        resultData["city"] = getCityName(ruleCondition.city)

    if ruleCondition.hostInvert == 1:
        resultData["host"] = "!=" + ruleCondition.host
    else:
        resultData["host"] = ruleCondition.host

    if ruleCondition.appidInvert == 1:
        resultData["appid"] = "!=" + ruleCondition.appid
    else:
        resultData["appid"] = ruleCondition.appid

    if ruleCondition.netInvert == 1:
        resultData["net"] = "!=" + getNetName(ruleCondition.net)
    else:
        resultData["net"] = getNetName(ruleCondition.net)

    resultData["is_use"] = rawResultData.is_use

    return resultData


# 删除条目（将is_use设置为0）
#
# post:
# id
#
# ret:
# result(操作成功)
@login_required
def ajRuleDelete(request):
    id = request.POST.get("id", "-1")
    # 查找该项目是否存在
    targetData = ServerRuleDat.objects.get(id=id)
    targetData.is_use = 0
    targetData.save()
    logRuleDelete(request, targetData.id)
    return_json = {'result': True}
    return JsonResponse(return_json)


# 启用条目(is_use 设置为1)
#
# post:
# id
#
# ret:
# result(操作成功
@login_required
def ajRuleReuse(request):
    id = request.POST.get("id", "-1")
    targetData = ServerRuleDat.objects.get(id=id)

    targetData.is_use = 1
    targetData.save()
    logRuleReuse(request, targetData.id)
    return_json = {'result': True}
    return JsonResponse(return_json)


# TODO reafactor
class GroupData:
    groupid = ""
    groupidName = ""


# 显示修改rule页面
#
# get:
# id(-1为新增，否则为修改操作)
#
# ret:
# condition(ruleCondition的默认参数)
# id(同上)
# allRule(数据库中所有rule数据)
# allCountry(数据库中所有国家信息，用来优化下拉框)
# allProvince(数据库中所有省份信息，用来优化下拉框)
# allCity(数据库中所有城市信息，用来优化下拉框)
# allNet(数据库中所有网络信息，用来优化下拉框)
# allGroup(数据库中所有服务器组信息，用来优化下拉框)
@login_required
def ruleConfigRevise(request):
    id = request.GET.get("id", "-1")

    condition = RuleCondition()

    # -1代表新增
    if id == "-1":
        id = -1
    else:
        rule = ServerRuleDat.objects.get(id=id)
        condition.initByStr(rule.rule)

    allCountry = CountryList.objects.all()
    allProvince = ProvList.objects.all()
    allCity = CityList.objects.all()
    allNet = NetList.objects.all()
    allRule = ServerRuleDat.objects.all()
    allGroup = ServerGroupDat.objects.all()

    allGroupid = []
    allGroupData = []
    for group in allGroup:
        if group.group_id not in allGroupid:
            groupData = GroupData()
            groupData.groupid = group.group_id
            groupData.groupidName = getServerGroupName(group.group_id)
            allGroupid.append(group.group_id)
            allGroupData.append(groupData)

    return render(request, "ruleConfig/ruleRevise.html",
                  {
                      "condition": condition,
                      "id": id,
                      "allRule": allRule,
                      "allCountry": allCountry,
                      "allProvince": allProvince,
                      "allCity": allCity,
                      "allNet": allNet,
                      "allGroup": allGroupData
                  })


# 接受表单，新增或更改rule数据
#
# post:
# id(-1为新增，否则为修改)
# country
# province
# city
# host
# appid
# net
# invertCountry(on为取反)
# invertProvince(on为取反)
# invertCity(on为取反)
# invertHost(on为取反)
# invertAppid(on为取反)
# invertNet(on为取反)
# rank
# ttl
# compel
# groupid
#
# ret:
# result(操作成功)
@login_required
def ajHandleRuleRevise(request):
    id = request.POST.get("id", "-1")

    condition = RuleCondition()
    condition.initByReq(request)
    # 拼接为rule字符串用来保存
    conditionStr = condition.convert2Str()

    rank = request.POST.get("rank", "")
    ttl = request.POST.get("ttl", "")
    compelStr = request.POST.get("compel", "")
    compel = 0
    if compelStr == 1:
        compel = 1
    groupid = request.POST.get("groupid", "")
    updateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    registrationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    # 查找该项目是否存在
    targetData = ServerRuleDat.objects.filter(id=id)

    if len(targetData) > 0:
        for data in targetData:
            data.update_time = updateTime
            data.group_id = groupid
            data.rule = conditionStr
            data.ttl = ttl
            data.compel = compel
            data.save()
            logRuleRevise(request, data.id)
    else:
        data = ServerRuleDat.objects.create(
            update_time=updateTime,
            registration_time=registrationTime,
            group_id=groupid,
            rule=conditionStr,
            rank=rank,
            ttl=ttl,
            compel=compel,
            is_use=1
        )
        logRuleNew(request, data.id)

    json_return = {'result': True}
    return JsonResponse(json_return)


# 搜索条件
conditions = []
# 0显示全部,1显示已启用,2显示未启用
showState = 0


# 显示rule搜索主页面，根据条件condition显示搜索结果result
@login_required
def ruleConfigSearch(request):
    # 搜索结果
    searchResult = []

    if request.method == "POST":
        # 将上次的搜索条件置空
        global showState
        global conditions
        del conditions[:]
        showState = 0

        ruleCondition = RuleCondition()
        ruleCondition.initByReq(request)

        conditions = ruleCondition.getSearchStrList()
        showState = request.POST.get("showState", 0)

    allRules = ServerRuleDat.objects.all()

    # 对于所有符合condition的rule添加到result列表中
    for rule in allRules:
        flag = True
        if rule.is_use == 0 and showState == "1":
            flag = False
        if rule.is_use == 1 and showState == "2":
            flag = False
        for condition in conditions:
            if rule.rule.find(condition) == -1:
                flag = False
        if flag:
            searchResult.append(convert2SearchResult(rule))

    allCountry = CountryList.objects.all()
    allProvince = ProvList.objects.all()
    allCity = CityList.objects.all()
    allNet = NetList.objects.all()
    resultSize = len(searchResult)

    paginator = Paginator(searchResult, 25)
    page = request.GET.get("page")
    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        result = paginator.page(1)
    except EmptyPage:
        result = paginator.page(paginator.num_pages)

    return render(request,
                  "ruleConfig/ruleSearch.html",
                  {"allCountry": allCountry,
                   "allProvince": allProvince,
                   "allCity": allCity,
                   "allNet": allNet,
                   "result": result,
                   "resultSize": resultSize
                   })
