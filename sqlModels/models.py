from __future__ import unicode_literals
from django.db import models


class CityList(models.Model):
    update_time = models.DateTimeField()
    registration_time = models.DateTimeField()
    code = models.IntegerField(unique=True)
    name = models.CharField(unique=True, max_length=32)
    prov_code = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'city_list'


class CountryList(models.Model):
    update_time = models.DateTimeField()
    registration_time = models.DateTimeField()
    code = models.IntegerField(unique=True)
    name = models.CharField(unique=True, max_length=32)

    class Meta:
        managed = False
        db_table = 'country_list'


class GroupList(models.Model):
    update_time = models.DateTimeField()
    registration_time = models.DateTimeField()
    name = models.CharField(unique=True, max_length=32)

    class Meta:
        managed = False
        db_table = 'group_list'


class IpSegDat(models.Model):
    update_time = models.DateTimeField()
    registration_time = models.DateTimeField()
    start_ip = models.IntegerField()
    end_ip = models.IntegerField()
    city_code = models.IntegerField()
    net_code = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ip_seg_dat'


class NetList(models.Model):
    update_time = models.DateTimeField()
    registration_time = models.DateTimeField()
    code = models.IntegerField(unique=True)
    name = models.CharField(unique=True, max_length=32)

    class Meta:
        managed = False
        db_table = 'net_list'


class ProvList(models.Model):
    update_time = models.DateTimeField()
    registration_time = models.DateTimeField()
    code = models.IntegerField(unique=True)
    name = models.CharField(unique=True, max_length=32)
    country_code = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'prov_list'


class ServerGroupDat(models.Model):
    update_time = models.DateTimeField()
    registration_time = models.DateTimeField()
    group_id = models.IntegerField()
    server_ids = models.TextField()
    time_out = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'server_group_dat'


class ServerList(models.Model):
    update_time = models.DateTimeField()
    registration_time = models.DateTimeField()
    ip = models.CharField(max_length=32)
    port = models.CharField(max_length=8)
    idc = models.CharField(max_length=16, blank=True, null=True)
    sign = models.CharField(max_length=32, blank=True, null=True)
    is_used = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'server_list'
        unique_together = (('ip', 'port'),)


class ServerRuleDat(models.Model):
#    id=models.IntegerField(primary_key=True,unique=True)
    update_time = models.DateTimeField()
    registration_time = models.DateTimeField()
    group_id = models.IntegerField()
    rule = models.CharField(max_length=256)
    rank = models.IntegerField()
    ttl = models.IntegerField()
    compel = models.IntegerField()
    is_use = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'server_rule_dat'
