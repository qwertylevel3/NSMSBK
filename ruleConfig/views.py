from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect
from sqlModels.models import ServerRuleDat
from sqlModels.models import CountryList
from sqlModels.models import CityList
from sqlModels.models import ProvList
from sqlModels.models import NetList
import time


class ServerRule:
    def __init__(self, ruleStr=""):
        self.country = ""
        self.province = ""
        self.city = ""
        self.host = ""
        self.appid = ""
        self.net = ""
        self.initByStr(ruleStr)

    #用一个rule字符设置内部数据,并自动填充空的country和province数据
    def initByStr(self,ruleStr):
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

    #转换为rule字符串
    def convert2Str(self):
        ruleStr = "&"

        if self.country != "":
            ruleStr = ("&country=" + self.country)
        if self.province != "":
            ruleStr = ("&province=" + self.province)
        if self.city != "":
            ruleStr = ("&city=" + self.city)
        if self.host != "":
            ruleStr += ("&host=" + self.host)
        if self.appid != "":
            ruleStr += ("&appid=" + self.appid)
        if self.net != "":
            ruleStr += ("&net=" + self.net)

        return ruleStr[1:]



# Create your views here.

def ruleConfigRevise(request):
    id = request.POST.get("id", "-1")

    ruleData = ServerRule()

    if id == "-1":
        id = -1
        for rule in ServerRuleDat.objects.all():
            if rule.id > id:
                id = rule.id
        id = id + 1
    else:
        rule = ServerRuleDat.objects.get(id=id)
        ruleData.initByStr(rule.rule)

    allCountry = CountryList.objects.all()
    allProvince = ProvList.objects.all()
    allCity = CityList.objects.all()
    allNet = NetList.objects.all()
    allRule = ServerRuleDat.objects.all()

    return render(request, "ruleConfig/ruleConfigRevise.html",
                  {
                      "ruleData": ruleData,
                      "id": id,
                      "allRule": allRule,
                      "allCountry": allCountry,
                      "allProvince": allProvince,
                      "allCity": allCity,
                      "allNet": allNet
                  })


def handleRuleRevise(request):
    if request.method != "POST":
        return ruleConfigRevise(request)

    ruleData = ServerRule()

    ruleData.city = request.POST.get("city", "")
    ruleData.province = request.POST.get("province", "")
    ruleData.country = request.POST.get("country", "")
    ruleData.host = request.POST.get("host", "")
    ruleData.appid = request.POST.get("appid", "")
    ruleData.net = request.POST.get("net", "")

    ruleStr = ruleData.convert2Str()

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

    targetData = ServerRuleDat.objects.filter(id=id)

    if len(targetData) > 0:
        for data in targetData:
            data.update_time = updateTime
            data.group_id = groupid
            data.rule = ruleStr
            data.ttl = ttl
            data.compel = compel
            data.save()
    else:
        ServerRuleDat.objects.create(
            update_time=updateTime,
            registration_time=registrationTime,
            group_id=groupid,
            rule=ruleStr,
            rank=rank,
            ttl=ttl,
            compel=compel,
            is_use=1
        )

    return HttpResponseRedirect('/ruleConfigSearch/')


def ruleConfigSearch(request):
    result = []
    if request.method == "POST":
        conditions = [""]

        city = request.POST.get("city", "")
        if city != "":
            conditions[0] = city

        province = request.POST.get("province", "")
        if province != "" and city == "":
            conditions[0] = province

        country = request.POST.get("country", "")
        if country != "" and city == "" and province == "":
            conditions[0] = country

        host = request.POST.get("host", "")
        if host != "":
            conditions.append("host=" + host)

        appid = request.POST.get("appid", "")
        if appid != "":
            conditions.append("appid=" + appid)

        net = request.POST.get("net", "")
        if net != "":
            conditions.append("net=" + net)

        allRules = ServerRuleDat.objects.all()

        size = len(ServerRuleDat.objects.all())

        for rule in allRules:
            flag = True
            for condition in conditions:
                if rule.is_use == 1 and rule.rule.find(condition) == -1:
                    flag = False
            if flag:
                result.append(rule)

    allCountry = CountryList.objects.all()
    allProvince = ProvList.objects.all()
    allCity = CityList.objects.all()
    allNet = NetList.objects.all()

    return render(request,
                  "ruleConfig/ruleConfigSearch.html",
                  {"allCountry": allCountry,
                   "allProvince": allProvince,
                   "allCity": allCity,
                   "allNet": allNet,
                   "result": result
                   })
