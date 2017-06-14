from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect
from sqlModels.models import ServerRuleDat
from sqlModels.models import CountryList
from sqlModels.models import CityList
from sqlModels.models import ProvList
from sqlModels.models import NetList
import time


def rule2Str(ruleData):
    ruleStr = "&"

    if ruleData["country"] != "":
        ruleStr = ("&country=" + ruleData["country"])
    elif ruleData["province"] != "":
        ruleStr = ("&province=" + ruleData["province"])
    elif ruleData["city"] != "":
        ruleStr = ("&city=" + ruleData["city"])

    if ruleData["host"]!="":
        ruleStr.join("&host="+ruleData["host"])
    if ruleData["appid"]!="":
        ruleStr.join("&appid="+ruleData["appid"])
    if ruleData["net"]!="":
        ruleStr.join("&net="+ruleData["net"])

    return ruleStr[1:]


# Create your views here.

def ruleConfigRevise(request):
    id = request.POST.get("id", "-1")

    ruleData = {
        "country": "",
        "province": "",
        "city": "",
        "host": "",
        "appid": "",
        "net": ""
    }
    if id == "-1":
        id = -1
        for rule in ServerRuleDat.objects.all():
            if rule.id > id:
                id = rule.id
        id = id + 1
    else:
        rule = ServerRuleDat.objects.get(id=id)

    allCountry = CountryList.objects.all()
    allProvince = ProvList.objects.all()
    allCity = CityList.objects.all()
    allNet = NetList.objects.all()
    allRule = ServerRuleDat.objects.all()

    return render(request, "ruleConfig/ruleConfigRevise.html",
                  {
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

    conditions = [""]



    city = request.POST.get("city", "")
    if city != "":
        conditions[0] = "city=" + city

    province = request.POST.get("province", "")
    if province != "" and city == "":
        conditions[0] = "province=" + province

    country = request.POST.get("country", "")
    if country != "" and city == "" and province == "":
        conditions[0] = "country=" + country

    host = request.POST.get("host", "")
    if host != "":
        conditions.append("host=" + host)

    appid = request.POST.get("appid", "")
    if appid != "":
        conditions.append("appid=" + appid)

    net = request.POST.get("net", "")
    if net != "":
        conditions.append("net=" + net)

    ruleStr = ""
    ruleStr += conditions[0]

    i = 1
    while i < len(conditions):
        ruleStr += "&" + conditions[i]
        i = i + 1

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
