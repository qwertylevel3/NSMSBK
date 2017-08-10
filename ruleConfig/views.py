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


# ���ݿ��ѯ����
# ����һЩ������ѯ�Ķ���������ҳ�����
class QueryBox(object):
    __instance = None
    countryMap = {}
    provinceMap = {}
    cityMap = {}
    serverGroupMap = {}
    netMap = {}

    def __init__(self):
        pass

    # ���ݹ��Ҵ��뷵�ع�������
    def getCountryName(self, countryID):
        if len(countryID) > 0:
            return self.countryMap[int(countryID)]
        return ""

    # ����ʡ�ݴ��뷵��ʡ������
    def getProvinceName(self, provinceID):
        if len(provinceID) > 0:
            return self.provinceMap[int(provinceID)]
        return ""

    # ���ݳ��д��뷵�س�������
    def getCityName(self, cityID):
        if len(cityID) > 0:
            return self.cityMap[int(cityID)]
        return ""

    # ���ݷ�������id���ط�����������
    def getServerGroupName(self, serverGroupID):
        if self.serverGroupMap.has_key(serverGroupID):
            return self.serverGroupMap[serverGroupID]
        return serverGroupID

    # ����������뷵����������
    def getNetName(self, netCode):
        if len(netCode) > 0:
            if self.netMap.has_key(int(netCode)):
                return self.netMap[int(netCode)]
        return netCode

    def initCountry(self):
        allCountry = CountryList.objects.all()
        self.countryMap = {}

        for country in allCountry:
            self.countryMap[country.code] = country.name

    def initProvince(self):
        allProvince = ProvList.objects.all()
        self.provinceMap = {}
        for province in allProvince:
            self.provinceMap[province.code] = province.name

    def initCity(self):
        allCity = CityList.objects.all()
        self.cityMap = {}
        for city in allCity:
            self.cityMap[city.code] = city.name

    def initServerGroup(self):
        allServerGroup = GroupList.objects.all()
        self.serverGroupMap = {}
        for serverGroup in allServerGroup:
            self.serverGroupMap[serverGroup.id] = serverGroup.name

    def initNetMap(self):
        allNet = NetList.objects.all()
        self.netMap = {}
        for net in allNet:
            self.netMap[net.code] = net.name

    def initMap(self):
        self.initProvince()
        self.initCountry()
        self.initCity()
        self.initServerGroup()
        self.initNetMap()

    def __new__(cls, *args, **kwd):
        if QueryBox.__instance is None:
            QueryBox.__instance = object.__new__(cls, *args, **kwd)
        return QueryBox.__instance


# ���ݹ��Ҵ��뷵�ع�������
def getCountryName(countryID):
    queryBox = QueryBox()
    return queryBox.getCountryName(countryID)


# ����ʡ�ݴ��뷵��ʡ������
def getProvinceName(provinceID):
    queryBox = QueryBox()
    return queryBox.getProvinceName(provinceID)


# ���ݳ��д��뷵�س�������
def getCityName(cityID):
    queryBox = QueryBox()
    return queryBox.getCityName(cityID)


# ���ݷ�������id���ط�����������
def getServerGroupName(serverGroupID):
    queryBox = QueryBox()
    return queryBox.getServerGroupName(serverGroupID)


# ����������뷵����������
def getNetName(netCode):
    queryBox = QueryBox()
    return queryBox.getNetName(netCode)


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

    if conditionStr == "":
        json_return = {'result': False, 'msg': "������Ϊ��"}
        return JsonResponse(json_return)

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
    # ÿ��ˢ��ҳ���ʱ������һ�»���
    queryBox = QueryBox()
    queryBox.initMap()

    allCountry = CountryList.objects.all()
    allProvince = ProvList.objects.all()
    allCity = CityList.objects.all()
    allNet = NetList.objects.all()
    allGroup = GroupList.objects.all()

    return render(request,
                  "ruleConfig/ruleSearch.html",
                  {"allCountry": allCountry,
                   "allProvince": allProvince,
                   "allCity": allCity,
                   "allNet": allNet,
                   "allGroup": allGroup
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
    queryBox = QueryBox()

    page = request.POST.get("page")
    serverGroup = request.POST.get("serverGroup", "")

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
        # if check(rule, conditions):
        #            searchResult.append(convert2SearchResult(rule))
        if serverGroup != "":
            if rule.group_id != int(serverGroup):
                continue
        if check(rule, ruleCondition):
            searchResult.append(convert2SearchResult(rule))

    return JsonResponse(result2dict(searchResult, page))
