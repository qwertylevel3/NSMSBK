from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect
from sqlModels.models import ServerRuleDat
from sqlModels.models import CountryList
from sqlModels.models import CityList
from sqlModels.models import ProvList
from sqlModels.models import NetList
import time


# Create your views here.


def ruleConfigAdd(request):
    if request.method=="POST":
        conditions=[""]

        city = request.POST.get("city", "")
        if city!="":
            conditions[0]="city="+city

        province = request.POST.get("province", "")
        if province != "" and city == "":
            conditions[0]="province="+province

        country = request.POST.get("country", "")
        if country != "" and city == "" and province == "":
            conditions[0]="country="+country

        host = request.POST.get("host", "")
        if host != "":
            conditions.append("host=" + host)

        appid = request.POST.get("appid", "")
        if appid != "":
            conditions.append("appid=" + appid)

        net = request.POST.get("net", "")
        if net != "":
            conditions.append("net=" + net)


        ruleStr=""
        ruleStr+=conditions[0]

        i=1
        while i<len(conditions):
            ruleStr+="&"+conditions[i]
            i=i+1

        rank=request.POST.get("rank","")
        ttl=request.POST.get("ttl","")
        compelStr=request.POST.get("compel","")
        compel=0
        if compelStr=="on":
            compel=1

        groupid=request.POST.get("groupid","")

        id=len(ServerRuleDat.objects.all())
        id=id+1

        updateTime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        registrationTime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))


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

    allCountry = CountryList.objects.all()
    allProvince = ProvList.objects.all()
    allCity = CityList.objects.all()
    allNet = NetList.objects.all()

    return render(request, "ruleConfig/ruleConfigAdd.html",
                  {
                      "allCountry":allCountry,
                      "allProvince":allProvince,
                      "allCity":allCity,
                      "allNet":allNet
                  })


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
