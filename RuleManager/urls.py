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
from django.views.generic.base import RedirectView

from RuleManager import settings


urlpatterns = [
    url(r'^admin/', admin.site.urls, name="admin"),
    url(r'^$', indexViews.index, name="root"),
    url(r'index/', indexViews.index, name="index"),

    url(r'^favicon\.ico$',RedirectView.as_view(url='static/favicon.ico',permanent=True)),

    url(r'^login/$', login, {'template_name': 'auth/login.html'}, name="login"),
    url(r'^logout/$', logout_then_login, name="logout"),
    url(r'check/', authViews.check, name="check"),

    url(r'ruleSearch/', ruleConfigViews.ruleSearch, name="ruleSearch"),
    url(r'ruleRevise/', ruleConfigViews.ruleConfigRevise, name="ruleRevise"),
    url(r'ajRuleDelete/', ruleConfigViews.ajRuleDelete, name="ajRuleDelete"),
    url(r'ajHandleRuleRevise/', ruleConfigViews.ajHandleRuleRevise, name="ajHandleRuleRevise"),
    url(r'ajRuleReuse/', ruleConfigViews.ajRuleReuse, name="ajRuleReuse"),
    url(r'ajRuleSearch/', ruleConfigViews.ajRuleSearch, name="ajRuleSearch"),

    url(r'serverSearch/', serverConfigViews.serverSearch, name="serverSearch"),
    url(r'serverRevise/', serverConfigViews.serverRevise, name="serverRevise"),

    url(r'ajServerSearch', serverConfigViews.ajServerSearch, name="ajServerSearch"),
    url(r'ajServerDelete/', serverConfigViews.ajServerDelete, name="ajServerDelete"),
    url(r'adHandleServerAdd/',serverConfigViews.ajHandleServerAdd,name="ajHandleServerAdd"),
    url(r'ajHandleServerRevise/', serverConfigViews.ajHandleServerRevise, name="ajHandleServerRevise"),
    url(r'ajServerReuse/', serverConfigViews.ajServerReuse, name="ajServerReuse"),
    url(r'ajValidateServer',serverConfigViews.ajValidateServer,name="ajValidateServer"),

    url(r'serverGroupSearch/', serverGroupConfigViews.serverGroupSearch, name="serverGroupSearch"),
    url(r'serverGroupRevise/', serverGroupConfigViews.serverGroupRevise, name="serverGroupRevise"),
    url(r'ajHandleServerGroupRevise/', serverGroupConfigViews.ajHandleServerGroupRevise,
        name="ajHandleServerGroupRevise"),
    url(r'ajServerGroupShowDetail/', serverGroupConfigViews.ajShowServerGroupDetail, name="ajServerGroupDetail"),
    url(r'ajInitServerGroupPage/', serverGroupConfigViews.ajInitServerGroupRevisePage, name="ajServerGroupReviseInit"),
]
