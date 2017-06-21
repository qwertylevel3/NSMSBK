from django.contrib import admin
from sqlModels.models import CityList
from sqlModels.models import ProvList
from sqlModels.models import CountryList
from sqlModels.models import GroupList
from sqlModels.models import IpSegDat
from sqlModels.models import NetList
from sqlModels.models import ServerGroupDat
from sqlModels.models import ServerList
from sqlModels.models import ServerRuleDat


# Register your models here.

admin.site.register(CityList)
admin.site.register(ProvList)
admin.site.register(CountryList)
admin.site.register(GroupList)
admin.site.register(IpSegDat)
admin.site.register(NetList)
admin.site.register(ServerGroupDat)
admin.site.register(ServerList)
admin.site.register(ServerRuleDat)



