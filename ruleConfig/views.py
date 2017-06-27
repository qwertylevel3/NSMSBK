from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from sqlModels.models import ServerRuleDat
from sqlModels.models import CountryList
from sqlModels.models import CityList
from sqlModels.models import ProvList
from sqlModels.models import NetList
from sqlModels.models import ServerGroupDat
from sqlModels.models import GroupList
import time
import logging

logger = logging.getLogger("sql")

class RuleCondition:
    def __init__(self, ruleStr=""):
        self.country = ""
        self.province = ""
        self.city = ""
        self.host = ""
        self.appid = ""
        self.net = ""
        self.initByStr(ruleStr)

    # 用一个rule字符设置内部数据,并自动填充空的country和province数据
    def initByStr(self, ruleStr):
        conditions = ruleStr.split("&")

        for condition in conditions:
            condition = condition.split("=")
            if condition[0] == "country":
                self.country = condition[1]
            if condition[0] == "province":
                self.province = condition[1]
            if condition[0] == "city":
                self.city = condition[1]
            if condition[0] == "host":
                self.host = condition[1]
            if condition[0] == "appid":
                self.appid = condition[1]
            if condition[0] == "net":
                self.net = condition[1]

        if self.city != "":
            self.province = self.city[0:5]
            self.country = self.city[0:3]
        elif self.province != "":
            self.country = self.province[0:3]

    # 转换为rule字符串
    def convert2Str(self):
        ruleStr = "&"

        if self.country != "":
            ruleStr = ("&country=" + self.country)
        if self.province != "":
            ruleStr = ("&province=" + self.province)
        if self.city != "":
            ruleStr = ("&city=" + self.city)

        if ruleStr == "&":
            ruleStr = ""

        if self.host != "":
            ruleStr += ("&host=" + self.host)
        if self.appid != "":
            ruleStr += ("&appid=" + self.appid)
        if self.net != "":
            ruleStr += ("&net=" + self.net)

        if ruleStr == "":
            return ruleStr
        else:
            return ruleStr[1:]

    # 查找字符串序列
    def getSearchStrList(self):
        conditions = [""]
        if self.city != "":
            conditions[0] = "=" + self.city
        if self.province != "" and self.city == "":
            conditions[0] = "=" + self.province
        if self.country != "" and self.city == "" and self.province == "":
            conditions[0] = "=" + self.country
        if self.host != "":
            conditions.append("host=" + self.host)
        if self.appid != "":
            conditions.append("appid=" + self.appid)
        if self.net != "":
            conditions.append("net=" + self.net)
        return conditions


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
    return HttpResponseRedirect('/ruleConfigSearch/')


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
    for group in allGroup:
        if group.group_id not in allGroupid:
            allGroupid.append(group.group_id)

    return render(request, "ruleConfig/ruleConfigRevise.html",
                  {
                      "condition": condition,
                      "id": id,
                      "allRule": allRule,
                      "allCountry": allCountry,
                      "allProvince": allProvince,
                      "allCity": allCity,
                      "allNet": allNet,
                      "allGroupid": allGroupid
                  })


# 接受表单，新增或更改rule数据
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
    else:
        ServerRuleDat.objects.create(
            update_time=updateTime,
            registration_time=registrationTime,
            group_id=groupid,
            rule=conditionStr,
            rank=rank,
            ttl=ttl,
            compel=compel,
            is_use=1
        )

    logger.info("test")

    return HttpResponseRedirect('/ruleConfigSearch/')


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
    if len(allServerGroup)>0:
        return allServerGroup[0].name
    return serverGroupID


# 将数据库数据转换为在search页面显示的数据项
def convert2SearchResult(rawResultData):
    resultData = {}
    ruleCondition = RuleCondition(rawResultData.rule)

    resultData["id"] = rawResultData.id
    resultData["group_id"] = getServerGroupName(rawResultData.group_id)
    resultData["rank"] = rawResultData.rank
    resultData["ttl"] = rawResultData.ttl
    resultData["compel"] = rawResultData.compel
    resultData["country"] = getCountryName(ruleCondition.country)
    resultData["province"] = getProvinceName(ruleCondition.province)
    resultData["city"] = getCityName(ruleCondition.city)
    resultData["host"] = ruleCondition.host
    resultData["appid"] = ruleCondition.appid
    resultData["net"] = ruleCondition.net

    return resultData


@login_required
def ruleConfigSearch(request):
    result = []
    conditions = []
    if request.method == "POST":
        ruleCondition = RuleCondition()

        ruleCondition.city = request.POST.get("city", "")
        ruleCondition.province = request.POST.get("province", "")
        ruleCondition.country = request.POST.get("country", "")
        ruleCondition.host = request.POST.get("host", "")
        ruleCondition.appid = request.POST.get("appid", "")
        ruleCondition.net = request.POST.get("net", "")

        conditions = ruleCondition.getSearchStrList()

    allRules = ServerRuleDat.objects.all()

    # 对于所有符合condition的rule添加到result列表中
    for rule in allRules:
        flag = True
        if rule.is_use == 0:
            flag = False
        for condition in conditions:
            if rule.rule.find(condition) == -1:
                flag = False
        if flag:
            result.append(convert2SearchResult(rule))

    allCountry = CountryList.objects.all()
    allProvince = ProvList.objects.all()
    allCity = CityList.objects.all()
    allNet = NetList.objects.all()
    resultSize = len(result)

    paginator = Paginator(result, 25)
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
