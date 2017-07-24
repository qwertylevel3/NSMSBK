# coding:gbk
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
    logger.info("%s : revise rule [%s]",
                request.user.username,
                ruleData2Str(rule))


# log规则新增
def logRuleNew(request, id):
    rule = ServerRuleDat.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : create rule [%s]",
                request.user.username,
                ruleData2Str(rule))


# log规则启用
def logRuleReuse(request, id):
    rule = ServerRuleDat.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : reuse rule [%s]",
                request.user.username,
                ruleData2Str(rule))


# log规则禁用
def logRuleDelete(request, id):
    rule = ServerRuleDat.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : delete rule [%s]",
                request.user.username,
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
        resultData["country"] = "~" + getCountryName(ruleCondition.country)
    else:
        resultData["country"] = getCountryName(ruleCondition.country)

    if ruleCondition.provinceInvert == 1:
        resultData["province"] = "~" + getProvinceName(ruleCondition.province)
    else:
        resultData["province"] = getProvinceName(ruleCondition.province)

    if ruleCondition.cityInvert == 1:
        resultData["city"] = "~" + getCityName(ruleCondition.city)
    else:
        resultData["city"] = getCityName(ruleCondition.city)

    if ruleCondition.hostInvert == 1:
        resultData["host"] = "~" + ruleCondition.host
    else:
        resultData["host"] = ruleCondition.host

    if ruleCondition.appidInvert == 1:
        resultData["appid"] = "~" + ruleCondition.appid
    else:
        resultData["appid"] = ruleCondition.appid

    if ruleCondition.netInvert == 1:
        resultData["net"] = "~" + getNetName(ruleCondition.net)
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


# 传递group信息用
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
def ruleRevise(request):
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
    if compelStr == "on":
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
            data.rank = rank
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


# 显示rule搜索主页面
#
# get:
#
# ret:
# allCountry(数据库中所有国家信息，用来优化下拉框)
# allProvince(数据库中所有省份信息，用来优化下拉框)
# allCity(数据库中所有城市信息，用来优化下拉框)
# allNet(数据库中所有网络信息，用来优化下拉框)
@login_required
def ruleSearch(request):
    allCountry = CountryList.objects.all()
    allProvince = ProvList.objects.all()
    allCity = CityList.objects.all()
    allNet = NetList.objects.all()

    return render(request,
                  "ruleConfig/ruleSearch.html",
                  {"allCountry": allCountry,
                   "allProvince": allProvince,
                   "allCity": allCity,
                   "allNet": allNet,
                   })


# result分页并序列化
def result2dict(searchResult, page):
    searchLen = len(searchResult)

    paginator = Paginator(searchResult, 25)
    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        result = paginator.page(1)
    except EmptyPage:
        result = paginator.page(paginator.num_pages)

    ruleList = []
    for rule in result:
        ruleList.append(rule)

    return {
        "searchLen": searchLen,
        "has_previous": result.has_previous(),
        "page_num": result.number,
        "has_next": result.has_next(),
        "all_page_num": result.paginator.num_pages,
        "ruleList": ruleList
    }

# 检查rule是否满足conditoin条件
# 用来搜索过程中过滤用
def check(rule, condition):
    tc = RuleCondition()
    tc.initByStr(rule.rule)

    # condition中需要检查net
    if condition.net != "":
        if tc.net != condition.net or tc.netInvert != condition.netInvert:
            return False
    # condition中需要检查appid
    if condition.appid != "":
        if tc.appid != condition.appid or tc.appidInvert != condition.appidInvert:
            return False
    # condition中需要检查host
    if condition.host != "":
        if tc.host != condition.host or tc.hostInvert != condition.hostInvert:
            return False
    # condition中有city
    if condition.city != "":
        if tc.city != condition.city or tc.cityInvert != condition.cityInvert:
            return False

    # condition中有province
    if condition.province != "":
        if tc.province != condition.province or tc.provinceInvert != condition.provinceInvert:
            return False

    # condition中有country
    if condition.country != "":
        if tc.country != condition.country or tc.countryInvert != condition.countryInvert:
            return False
    return True


# 根据提交的rule条件搜索所有对应的rule
#
# post:
# showState(显示条件：0显示所有,1显示已启用,2显示未启用)
# page(结果中第几页，以25个一页计)
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
#
# ret:
# has_previous(true存在上一页，false不存在上一页)
# page_num(当前是第几页)
# has_next(true存在下一页，false不存在下一页)
# all_page_num(一共有多少页)
# ruleList(rule组成的列表)
@login_required
def ajRuleSearch(request):
    page = request.POST.get("page")
    searchResult = []

    ruleCondition = RuleCondition()
    ruleCondition.initByReq(request)

    showState = request.POST.get("showState", 0)

    allRules = ServerRuleDat.objects.all()

    # 对于所有符合condition的rule添加到result列表中
    for rule in allRules:
        if rule.is_use == 0 and showState == "1":
            continue
        if rule.is_use == 1 and showState == "2":
            continue
        #        if check(rule, conditions):
        #            searchResult.append(convert2SearchResult(rule))
        if check(rule, ruleCondition):
            searchResult.append(convert2SearchResult(rule))

    return JsonResponse(result2dict(searchResult, page))
