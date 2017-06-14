from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect
from sqlModels.models import ServerRuleDat
from sqlModels.models import CountryList
from sqlModels.models import CityList
from sqlModels.models import ProvList
from sqlModels.models import NetList
import time



#辅助函数
#规则map拼接为字符串
def ruleData2ruleStr(ruleData):
    ruleStr = "&"

    if ruleData["country"] != "":
        ruleStr = ("&country=" + ruleData["country"])
    if ruleData["province"] != "":
        ruleStr = ("&province=" + ruleData["province"])
    if ruleData["city"] != "":
        ruleStr = ("&city=" + ruleData["city"])

    if ruleData["host"] != "":
        ruleStr+=("&host=" + ruleData["host"])
    if ruleData["appid"] != "":
        ruleStr+=("&appid=" + ruleData["appid"])
    if ruleData["net"] != "":
        ruleStr+=("&net=" + ruleData["net"])

    return ruleStr[1:]


#辅助函数
#规则字符串转换为map数据，根据城市，省份，自动填充省份，国家数据
def ruleStr2ruleData(ruleStr):
    ruleData = {
        "country": "",
        "province": "",
        "city": "",
        "host": "",
        "appid": "",
        "net": ""
    }

    conditions=ruleStr.split("&")

    for condition in conditions:
        condition=condition.split("=")
        ruleData[condition[0]]=condition[1]

    if ruleData["city"]!="":
        ruleData["province"]=ruleData["city"][0:5]
        ruleData["country"]=ruleData["city"][0:3]
    elif ruleData["province"]!="":
        ruleData["country"]=ruleData["province"][0:3]

    return ruleData



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
        ruleData=ruleStr2ruleData(rule.rule)

    allCountry = CountryList.objects.all()
    allProvince = ProvList.objects.all()
    allCity = CityList.objects.all()
    allNet = NetList.objects.all()
    allRule = ServerRuleDat.objects.all()


    return render(request, "ruleConfig/ruleConfigRevise.html",
                  {
                      "ruleData":ruleData,
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

    ruleData = {}

    ruleData["city"] = request.POST.get("city", "")
    ruleData["province"] = request.POST.get("province", "")
    ruleData["country"] = request.POST.get("country", "")
    ruleData["host"] = request.POST.get("host", "")
    ruleData["appid"] = request.POST.get("appid", "")
    ruleData["net"] = request.POST.get("net", "")

    ruleStr = ruleData2ruleStr(ruleData)

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
