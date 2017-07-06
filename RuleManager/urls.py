"""RuleManager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from indexPage import views as indexViews
from ruleConfig import views as ruleConfigViews
from serverConfig import views as serverConfigViews
from serverGroupConfig import views as serverGroupConfigViews
from myAuthority import views as authViews
from django.contrib.auth.views import login, logout_then_login

urlpatterns = [
    url(r'^admin/', admin.site.urls, name="admin"),
    url(r'index/', indexViews.index, name="index"),

    url(r'^login/$', login, {'template_name': 'auth/login.html'}, name="login"),
    url(r'^logout/$', logout_then_login, name="logout"),
    url(r'check/', authViews.check, name="check"),

    url(r'ruleConfigSearch/', ruleConfigViews.ruleConfigSearch, name="ruleSearch"),
    url(r'ruleConfigRevise/', ruleConfigViews.ruleConfigRevise, name="ruleRevise"),
    url(r'ruleConfigDelete/', ruleConfigViews.ajRuleDelete, name="ruleDelete"),
    url(r'handleRuleRevise/', ruleConfigViews.ajHandleRuleRevise, name="handleRuleRevise"),
    url(r'ruleConfigReuse/', ruleConfigViews.ajRuleReuse, name="ruleReuse"),

    url(r'serverSearch/', serverConfigViews.serverSearch, name="serverSearch"),
    url(r'serverRevise/', serverConfigViews.serverRevise, name="serverRevise"),
    url(r'ajServerSearch', serverConfigViews.ajServerSearch, name="ajServerSearch"),
    url(r'ajServerDelete/', serverConfigViews.ajServerDelete, name="ajServerDelete"),
    url(r'ajHandleServerRevise/', serverConfigViews.ajHandleServerRevise, name="ajHandleServerRevise"),
    url(r'ajServerReuse/', serverConfigViews.ajServerReuse, name="ajServerReuse"),

    url(r'serverGroupSearch/', serverGroupConfigViews.serverGroupSearch, name="serverGroupSearch"),
    url(r'serverGroupRevise/', serverGroupConfigViews.serverGroupConfigRevise, name="serverGroupRevise"),
    url(r'ajHandleServerGroupRevise/', serverGroupConfigViews.ajHandleServerGroupRevise,
        name="ajHandleServerGroupRevise"),
    url(r'ajServerGroupShowDetail/', serverGroupConfigViews.ajShowServerGroupDetail, name="ajServerGroupDetail"),
    url(r'ajInitServerGroupPage/', serverGroupConfigViews.ajInitServerGroupRevisePage, name="ajServerGroupReviseInit"),
]
