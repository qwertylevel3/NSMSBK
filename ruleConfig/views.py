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


# ���ݿ�rule��Ϣת��Ϊ�ַ���������log
def ruleData2Str(ruleData):
    ruleStr = ""
    ruleStr += "id:" + str(ruleData.id) + "|"
    ruleStr += "group_id:" + str(ruleData.group_id) + "|"
    ruleStr += "rule:" + ruleData.rule + "|"
    ruleStr += "rank:" + str(ruleData.rank) + "|"
    ruleStr += "ttl:" + str(ruleData.ttl) + "|"
    ruleStr += "compel:" + str(ruleData.compel)
    return ruleStr


# log�������
def logRuleRevise(request, id):
    rule = ServerRuleDat.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : revise rule [%s]",
                request.user.username,
                ruleData2Str(rule))


# log��������
def logRuleNew(request, id):
    rule = ServerRuleDat.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : create rule [%s]",
                request.user.username,
                ruleData2Str(rule))


# log��������
def logRuleReuse(request, id):
    rule = ServerRuleDat.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : reuse rule [%s]",
                request.user.username,
                ruleData2Str(rule))


# log�������
def logRuleDelete(request, id):
    rule = ServerRuleDat.objects.get(id=id)
    logger = logging.getLogger("sql")
    logger.info("%s : delete rule [%s]",
                request.user.username,
                ruleData2Str(rule))


# ���ݹ��Ҵ��뷵�ع�������
def getCountryName(countryID):
    if len(countryID) > 0:
        country = CountryList.objects.get(code=int(countryID))
        return country.name
    return ""


# ����ʡ�ݴ��뷵��ʡ������
def getProvinceName(provinceID):
    if len(provinceID) > 0:
        province = ProvList.objects.get(code=int(provinceID))
        return province.name
    return ""


# ���ݳ��д��뷵�س�������
def getCityName(cityID):
    if len(cityID) > 0:
        city = CityList.objects.get(code=int(cityID))
        return city.name
    return ""


# ���ݷ�������id���ط�����������
def getServerGroupName(serverGroupID):
    allServerGroup = GroupList.objects.filter(id=serverGroupID)
    if len(allServerGroup) > 0:
        return allServerGroup[0].name
    return serverGroupID


# ����������뷵����������
def getNetName(netCode):
    if len(netCode) > 0:
        net = NetList.objects.filter(code=netCode)
        if len(net) > 0:
            return net[0].name
    return netCode


# �����ݿ�����ת��Ϊ��searchҳ����ʾ��������
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


# ɾ����Ŀ����is_use����Ϊ0��
#
# post:
# id
#
# ret:
# result(�����ɹ�)
@login_required
def ajRuleDelete(request):
    id = request.POST.get("id", "-1")
    # ���Ҹ���Ŀ�Ƿ����
    targetData = ServerRuleDat.objects.get(id=id)
    targetData.is_use = 0
    targetData.save()
    logRuleDelete(request, targetData.id)
    return_json = {'result': True}
    return JsonResponse(return_json)


# ������Ŀ(is_use ����Ϊ1)
#
# post:
# id
#
# ret:
# result(�����ɹ�
@login_required
def ajRuleReuse(request):
    id = request.POST.get("id", "-1")
    targetData = ServerRuleDat.objects.get(id=id)

    targetData.is_use = 1
    targetData.save()
    logRuleReuse(request, targetData.id)
    return_json = {'result': True}
    return JsonResponse(return_json)


# ����group��Ϣ��
class GroupData:
    groupid = ""
    groupidName = ""


# ��ʾ�޸�ruleҳ��
#
# get:
# id(-1Ϊ����������Ϊ�޸Ĳ���)
#
# ret:
# condition(ruleCondition��Ĭ�ϲ���)
# id(ͬ��)
# allRule(���ݿ�������rule����)
# allCountry(���ݿ������й�����Ϣ�������Ż�������)
# allProvince(���ݿ�������ʡ����Ϣ�������Ż�������)
# allCity(���ݿ������г�����Ϣ�������Ż�������)
# allNet(���ݿ�������������Ϣ�������Ż�������)
# allGroup(���ݿ������з���������Ϣ�������Ż�������)
@login_required
def ruleRevise(request):
    id = request.GET.get("id", "-1")

    condition = RuleCondition()

    # -1��������
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


# ���ܱ������������rule����
#
# post:
# id(-1Ϊ����������Ϊ�޸�)
# country
# province
# city
# host
# appid
# net
# invertCountry(onΪȡ��)
# invertProvince(onΪȡ��)
# invertCity(onΪȡ��)
# invertHost(onΪȡ��)
# invertAppid(onΪȡ��)
# invertNet(onΪȡ��)
# rank
# ttl
# compel
# groupid
#
# ret:
# result(�����ɹ�)
@login_required
def ajHandleRuleRevise(request):
    id = request.POST.get("id", "-1")

    condition = RuleCondition()
    condition.initByReq(request)
    # ƴ��Ϊrule�ַ�����������
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

    # ���Ҹ���Ŀ�Ƿ����
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


# ��ʾrule������ҳ��
#
# get:
#
# ret:
# allCountry(���ݿ������й�����Ϣ�������Ż�������)
# allProvince(���ݿ�������ʡ����Ϣ�������Ż�������)
# allCity(���ݿ������г�����Ϣ�������Ż�������)
# allNet(���ݿ�������������Ϣ�������Ż�������)
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


# result��ҳ�����л�
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

# ���rule�Ƿ�����conditoin����
# �������������й�����
def check(rule, condition):
    tc = RuleCondition()
    tc.initByStr(rule.rule)

    # condition����Ҫ���net
    if condition.net != "":
        if tc.net != condition.net or tc.netInvert != condition.netInvert:
            return False
    # condition����Ҫ���appid
    if condition.appid != "":
        if tc.appid != condition.appid or tc.appidInvert != condition.appidInvert:
            return False
    # condition����Ҫ���host
    if condition.host != "":
        if tc.host != condition.host or tc.hostInvert != condition.hostInvert:
            return False
    # condition����city
    if condition.city != "":
        if tc.city != condition.city or tc.cityInvert != condition.cityInvert:
            return False

    # condition����province
    if condition.province != "":
        if tc.province != condition.province or tc.provinceInvert != condition.provinceInvert:
            return False

    # condition����country
    if condition.country != "":
        if tc.country != condition.country or tc.countryInvert != condition.countryInvert:
            return False
    return True


# �����ύ��rule�����������ж�Ӧ��rule
#
# post:
# showState(��ʾ������0��ʾ����,1��ʾ������,2��ʾδ����)
# page(����еڼ�ҳ����25��һҳ��)
# country
# province
# city
# host
# appid
# net
# invertCountry(onΪȡ��)
# invertProvince(onΪȡ��)
# invertCity(onΪȡ��)
# invertHost(onΪȡ��)
# invertAppid(onΪȡ��)
# invertNet(onΪȡ��)
#
# ret:
# has_previous(true������һҳ��false��������һҳ)
# page_num(��ǰ�ǵڼ�ҳ)
# has_next(true������һҳ��false��������һҳ)
# all_page_num(һ���ж���ҳ)
# ruleList(rule��ɵ��б�)
@login_required
def ajRuleSearch(request):
    page = request.POST.get("page")
    searchResult = []

    ruleCondition = RuleCondition()
    ruleCondition.initByReq(request)

    showState = request.POST.get("showState", 0)

    allRules = ServerRuleDat.objects.all()

    # �������з���condition��rule��ӵ�result�б���
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
