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


def ruleData2Str(ruleData):
    ruleStr = ""
    ruleStr += "id:" + str(ruleData.id) + "|"
    ruleStr += "group_id:" + str(ruleData.group_id) + "|"
    ruleStr += "rule:" + ruleData.rule + "|"
    ruleStr += "rank:" + str(ruleData.rank) + "|"
    ruleStr += "ttl:" + str(ruleData.ttl) + "|"
    ruleStr += "compel:" + str(ruleData.compel)
    return ruleStr


def logRuleRevise(request, id):
    rule = ServerRuleDat.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : revise rule %s[%s]",
                request.user.username,
                id,
                ruleData2Str(rule))


def logRuleNew(request, id):
    rule = ServerRuleDat.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : create rule %s[%s]",
                request.user.username,
                id,
                ruleData2Str(rule))

def logRuleReuse(request,id):
    rule = ServerRuleDat.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : reuse rule %s[%s]",
                request.user.username,
                id,
                ruleData2Str(rule))

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


# rule匹配规则的六个项的抽象
# 主要处理六个条件的拼接合并分离以及字符串转换等操作
# 每个条件可以是反条件
# 反条件用!=,方便字符串切分
class RuleCondition:
    def __init__(self, ruleStr=""):
        self.country = ""
        self.province = ""
        self.city = ""
        self.host = ""
        self.appid = ""
        self.net = ""
        self.countryInvert = 0
        self.provinceInvert = 0
        self.cityInvert = 0
        self.hostInvert = 0
        self.appidInvert = 0
        self.netInvert = 0
        self.initByStr(ruleStr)

    # 用一个rule字符设置内部数据,并自动填充空的country和province数据
    def initByStr(self, ruleStr):
        conditions = ruleStr.split("&")

        for condition in conditions:
            condition = condition.split("=")

            if condition[0] == "country":
                self.country = condition[1]
                self.countryInvert = 0
            elif condition[0] == "country!":
                self.country = condition[1]
                self.countryInvert = 1

            if condition[0] == "province":
                self.province = condition[1]
                self.provinceInvert = 0
            elif condition[0] == "province!":
                self.province = condition[1]
                self.provinceInvert = 1

            if condition[0] == "city":
                self.city = condition[1]
                self.cityInvert = 0
            elif condition[0] == "city!":
                self.city = condition[1]
                self.cityInvert = 1

            if condition[0] == "host":
                self.host = condition[1]
                self.hostInvert = 0
            elif condition[0] == "host!":
                self.host = condition[1]
                self.hostInvert = 1

            if condition[0] == "appid":
                self.appid = condition[1]
                self.appidInvert = 0
            elif condition[0] == "appid!":
                self.appid = condition[1]
                self.appidInvert = 1

            if condition[0] == "net":
                self.net = condition[1]
                self.netInvert = 0
            elif condition[0] == "net!":
                self.net = condition[1]
                self.netInvert = 1

        if self.city != "":
            self.province = self.city[0:5]
            self.country = self.city[0:3]
        elif self.province != "":
            self.country = self.province[0:3]

    # 转换为rule字符串
    def convert2Str(self):
        ruleStr = "&"

        if self.country != "" and self.countryInvert == 0:
            ruleStr = ("&country=" + self.country)
        elif self.country != "" and self.countryInvert == 1:
            ruleStr = ("&country!=" + self.country)
        if self.province != "" and self.provinceInvert == 0:
            ruleStr = ("&province=" + self.province)
        elif self.province != "" and self.provinceInvert == 1:
            ruleStr = ("&province!=" + self.province)
        if self.city != "" and self.cityInvert == 0:
            ruleStr = ("&city=" + self.city)
        elif self.city != "" and self.cityInvert == 1:
            ruleStr = ("&city!=" + self.city)

        if ruleStr == "&":
            ruleStr = ""

        if self.host != "" and self.hostInvert == 0:
            ruleStr += ("&host=" + self.host)
        elif self.host != "" and self.hostInvert == 1:
            ruleStr += ("&host!=" + self.host)
        if self.appid != "" and self.appidInvert == 0:
            ruleStr += ("&appid=" + self.appid)
        elif self.appid != "" and self.appidInvert == 1:
            ruleStr += ("&appid!=" + self.appid)
        if self.net != "" and self.netInvert == 0:
            ruleStr += ("&net=" + self.net)
        elif self.net != "" and self.netInvert == 1:
            ruleStr += ("&net!=" + self.net)

        if ruleStr == "":
            return ruleStr
        else:
            return ruleStr[1:]

    # 查找字符串序列
    def getSearchStrList(self):
        conditions = [""]
        if self.city != "" and self.cityInvert == 0:
            conditions[0] = "=" + self.city
        elif self.city != "" and self.cityInvert == 1:
            conditions[0] = "!=" + self.city

        if self.province != "" and self.city == "" and self.provinceInvert == 0:
            conditions[0] = "=" + self.province
        elif self.province != "" and self.city == "" and self.provinceInvert == 1:
            conditions[0] = "!=" + self.province

        if self.country != "" and self.city == "" and self.province == "" and self.countryInvert == 0:
            conditions[0] = "=" + self.country
        elif self.country != "" and self.city == "" and self.province == "" and self.countryInvert == 1:
            conditions[0] = "!=" + self.country

        if self.host != "" and self.hostInvert == 0:
            conditions.append("host=" + self.host)
        elif self.host != "" and self.hostInvert == 1:
            conditions.append("host!=" + self.host)

        if self.appid != "" and self.appidInvert == 0:
            conditions.append("appid=" + self.appid)
        elif self.appid != "" and self.appidInvert == 1:
            conditions.append("appid!=" + self.appid)

        if self.net != "" and self.netInvert == 0:
            conditions.append("net=" + self.net)
        elif self.net != "" and self.netInvert == 1:
            conditions.append("net!=" + self.net)
        return conditions


# 删除条目（将is_use设置为0）
@login_required
def ruleConfigDelete(request):
    id = request.POST.get("id", "-1")
    # 查找该项目是否存在
    targetData = ServerRuleDat.objects.filter(id=id)

    # 查找成功则设置isuse为0，作为删除操作
    if len(targetData) > 0:
        for data in targetData:
            data.is_use = 0
            data.save()
            logRuleDelete(request, data.id)
            return_json={'result':True}
            return JsonResponse(return_json)
    return_json={'result':False}
    return JsonResponse(return_json)

# 启用条目(is_use 设置为1)
@login_required
def ruleConfigReuse(request):
    id = request.POST.get("id", "-1")
    # 查找该项目是否存在
    targetData = ServerRuleDat.objects.filter(id=id)

    # 查找成功则设置isuse为1，作为启用操作
    if len(targetData) > 0:
        for data in targetData:
            data.is_use = 1
            data.save()
            logRuleReuse(request, data.id)
            return_json={'result':True}
            return JsonResponse(return_json)
    return_json={'result':False}
    return JsonResponse(return_json)

class GroupData:
    groupid = ""
    groupidName = ""


# 显示修改rule页面
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

    return render(request, "ruleConfig/ruleConfigRevise.html",
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
# 如果表单中id为-1代表新增数据，否则为更改数据
@login_required
def handleRuleRevise(request):
    if request.method != "POST":
        return HttpResponseRedirect('/ruleConfigSearch/')

    condition = RuleCondition()
    condition.city = request.POST.get("city", "")
    condition.province = request.POST.get("province", "")
    condition.country = request.POST.get("country", "")
    condition.host = request.POST.get("host", "")
    condition.appid = request.POST.get("appid", "")
    condition.net = request.POST.get("net", "")

    if request.POST.get("countryInvert", "off") == "on":
        condition.countryInvert = 1
    if request.POST.get("provinceInvert", "off") == "on":
        condition.provinceInvert = 1
    if request.POST.get("cityInvert", "off") == "on":
        condition.cityInvert = 1
    if request.POST.get("hostInvert", "off") == "on":
        condition.hostInvert = 1
    if request.POST.get("appidInvert", "off") == "on":
        condition.appidInvert = 1
    if request.POST.get("netInvert", "off") == "on":
        condition.netInvert = 1

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

    id = request.POST.get("id", "-1")

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

    return HttpResponseRedirect('/ruleConfigSearch/')


# 将数据库数据转换为在search页面显示的数据项
def convert2SearchResult(rawResultData):
    resultData = {}
    ruleCondition = RuleCondition(rawResultData.rule)

    resultData["id"] = rawResultData.id
    resultData["group_id"] = getServerGroupName(rawResultData.group_id)
    resultData["rank"] = rawResultData.rank
    resultData["ttl"] = rawResultData.ttl
    resultData["compel"] = rawResultData.compel

    if ruleCondition.countryInvert==1:
        resultData["country"]="!="+getCountryName(ruleCondition.country)
    else:
        resultData["country"] = getCountryName(ruleCondition.country)

    if ruleCondition.provinceInvert==1:
        resultData["province"] ="!="+ getProvinceName(ruleCondition.province)
    else:
        resultData["province"] =getProvinceName(ruleCondition.province)

    if ruleCondition.cityInvert==1:
        resultData["city"] = "!="+ getCityName(ruleCondition.city)
    else:
        resultData["city"] = getCityName(ruleCondition.city)

    if ruleCondition.hostInvert==1:
        resultData["host"] = "!="+ruleCondition.host
    else:
        resultData["host"] = ruleCondition.host

    if ruleCondition.appidInvert==1:
        resultData["appid"] = "!="+ruleCondition.appid
    else:
        resultData["appid"] = ruleCondition.appid

    if ruleCondition.netInvert==1:
        resultData["net"] = "!="+getNetName(ruleCondition.net)
    else:
        resultData["net"] = getNetName(ruleCondition.net)

    resultData["is_use"] = rawResultData.is_use

    return resultData


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
        ruleCondition.city = request.POST.get("city", "")
        ruleCondition.province = request.POST.get("province", "")
        ruleCondition.country = request.POST.get("country", "")
        ruleCondition.host = request.POST.get("host", "")
        ruleCondition.appid = request.POST.get("appid", "")
        ruleCondition.net = request.POST.get("net", "")

        if request.POST.get("countryInvert", "off") == "on":
            ruleCondition.countryInvert = 1
        if request.POST.get("provinceInvert", "off") == "on":
            ruleCondition.provinceInvert = 1
        if request.POST.get("cityInvert", "off") == "on":
            ruleCondition.cityInvert = 1
        if request.POST.get("hostInvert", "off") == "on":
            ruleCondition.hostInvert = 1
        if request.POST.get("appidInvert", "off") == "on":
            ruleCondition.appidInvert = 1
        if request.POST.get("netInvert", "off") == "on":
            ruleCondition.netInvert = 1

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
                  "ruleConfig/ruleConfigSearch.html",
                  {"allCountry": allCountry,
                   "allProvince": allProvince,
                   "allCity": allCity,
                   "allNet": allNet,
                   "result": result,
                   "resultSize": resultSize
                   })
