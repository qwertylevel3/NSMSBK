# rule匹配规则的六个项的抽象
# 主要处理六个条件的拼接合并分离以及字符串转换等操作
# 每个条件可以是反条件
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

    # 用request初始化数据,并自动填充空的country和province数据
    def initByReq(self, request):
        self.city = request.POST.get("city", "")
        self.province = request.POST.get("province", "")
        self.country = request.POST.get("country", "")
        self.host = request.POST.get("host", "")
        self.appid = request.POST.get("appid", "")
        self.net = request.POST.get("net", "")

        if request.POST.get("countryInvert", "off") == "on":
            self.countryInvert = 1
        if request.POST.get("provinceInvert", "off") == "on":
            self.provinceInvert = 1
        if request.POST.get("cityInvert", "off") == "on":
            self.cityInvert = 1
        if request.POST.get("hostInvert", "off") == "on":
            self.hostInvert = 1
        if request.POST.get("appidInvert", "off") == "on":
            self.appidInvert = 1
        if request.POST.get("netInvert", "off") == "on":
            self.netInvert = 1

        if self.city != "":
            self.province = self.city[0:5]
            self.country = self.city[0:3]
        elif self.province != "":
            self.country = self.province[0:3]

        self.host=self.host.strip()
        self.appid=self.appid.strip()

    # 用一个rule字符设置内部数据,并自动填充空的country和province数据
    def initByStr(self, ruleStr):
        conditionStrList = ruleStr.split("&")

        for conditionStr in conditionStrList:
            if conditionStr.find("=")!=-1:
                conditionStr = conditionStr.split("=")
                if conditionStr[0] == "country":
                    self.country = conditionStr[1]
                    self.countryInvert = 0
                if conditionStr[0] == "province":
                    self.province = conditionStr[1]
                    self.provinceInvert = 0
                if conditionStr[0] == "city":
                    self.city = conditionStr[1]
                    self.cityInvert = 0
                if conditionStr[0] == "host":
                    self.host = conditionStr[1]
                    self.hostInvert = 0
                if conditionStr[0] == "appid":
                    self.appid = conditionStr[1]
                    self.appidInvert = 0
                if conditionStr[0] == "net":
                    self.net = conditionStr[1]
                    self.netInvert = 0
            elif conditionStr.find("~")!=-1:
                conditionStr = conditionStr.split("~")
                if conditionStr[0] == "country":
                    self.country = conditionStr[1]
                    self.countryInvert = 1
                if conditionStr[0] == "province":
                    self.province = conditionStr[1]
                    self.provinceInvert = 1
                if conditionStr[0] == "city":
                    self.city = conditionStr[1]
                    self.cityInvert = 1
                if conditionStr[0] == "host":
                    self.host = conditionStr[1]
                    self.hostInvert = 1
                if conditionStr[0] == "appid":
                    self.appid = conditionStr[1]
                    self.appidInvert = 1
                if conditionStr[0] == "net":
                    self.net = conditionStr[1]
                    self.netInvert = 1

        if self.city != "":
            self.province = self.city[0:5]
            self.country = self.city[0:3]
        elif self.province != "":
            self.country = self.province[0:3]

        self.host=self.host.strip()
        self.appid=self.appid.strip()

    # 转换为rule字符串
    def convert2Str(self):
        ruleStr = "&"

        if self.country != "" and self.countryInvert == 0:
            ruleStr = ("&country=" + self.country)
        elif self.country != "" and self.countryInvert == 1:
            ruleStr = ("&country~" + self.country)
        if self.province != "" and self.provinceInvert == 0:
            ruleStr = ("&province=" + self.province)
        elif self.province != "" and self.provinceInvert == 1:
            ruleStr = ("&province~" + self.province)
        if self.city != "" and self.cityInvert == 0:
            ruleStr = ("&city=" + self.city)
        elif self.city != "" and self.cityInvert == 1:
            ruleStr = ("&city~" + self.city)

        if ruleStr == "&":
            ruleStr = ""

        if self.host != "" and self.hostInvert == 0:
            ruleStr += ("&host=" + self.host)
        elif self.host != "" and self.hostInvert == 1:
            ruleStr += ("&host~" + self.host)
        if self.appid != "" and self.appidInvert == 0:
            ruleStr += ("&appid=" + self.appid)
        elif self.appid != "" and self.appidInvert == 1:
            ruleStr += ("&appid~" + self.appid)
        if self.net != "" and self.netInvert == 0:
            ruleStr += ("&net=" + self.net)
        elif self.net != "" and self.netInvert == 1:
            ruleStr += ("&net~" + self.net)

        if ruleStr == "":
            return ruleStr
        else:
            return ruleStr[1:]
