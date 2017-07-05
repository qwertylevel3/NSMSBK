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
    url(r'^admin/', admin.site.urls,name="admin"),
    url(r'index/', indexViews.index,name="index"),

    url(r'^login/$', login, {'template_name': 'auth/login.html'},name="login"),  # 指定登录页面模板
    url(r'^logout/$', logout_then_login,name="logout"),  # 退出登录，并跳转到登录页面
    url(r'check/', authViews.check,name="check"),

    url(r'ruleConfigSearch/', ruleConfigViews.ruleConfigSearch,name="ruleSearch"),
    url(r'ruleConfigRevise/', ruleConfigViews.ruleConfigRevise,name="ruleRevise"),
    url(r'ruleConfigDelete/', ruleConfigViews.ruleConfigDelete,name="ruleDelete"),
    url(r'handleRuleRevise/', ruleConfigViews.handleRuleRevise,name="handleRuleRevise"),
    url(r'ruleConfigReuse/', ruleConfigViews.ruleConfigReuse,name="ruleReuse"),

    url(r'serverConfigSearch/', serverConfigViews.serverConfigSearch,name="serverSearch"),
    url(r'serverConfigRevise/', serverConfigViews.serverConfigRevise,name="serverRevise"),
    url(r'serverConfigDelete/', serverConfigViews.serverConfigDelete,name="serverDelete"),
    url(r'handleServerRevise/', serverConfigViews.handleServerRevise,name="handleServerRevise"),
    url(r'serverConfigReuse/', serverConfigViews.serverConfigReuse,name="serverReuse"),

    url(r'serverGroupConfigSearch/', serverGroupConfigViews.serverGroupConfigSearch,name="serverGroupSearch"),
    url(r'serverGroupConfigRevise/', serverGroupConfigViews.serverGroupConfigRevise,name="serverGroupRevise"),
    url(r'handleServerGroupRevise/', serverGroupConfigViews.handleServerGroupRevise,name="handleServerGroupRevise"),
    url(r'serverGroupShowDetail/', serverGroupConfigViews.showServerGroupDetail,name="serverGroupDetail"),
    url(r'initServerGroupConfigPage/',serverGroupConfigViews.initServerGroupConfigPage,name="serverGroupReviseInit"),
]
