
# NameServerMngrSite
* 环境：ubuntu12.04 apache2.2.22


### 自动部署
```bash
chmod u+x setup.sh
su root
./setup.sh
```


### 手动部署

#### 目录结构
```
/NameServerMngrSite
    |--...
    |--/NameServerMngrSite
    |    |--__init__.py
    |    |--settings.py
    |    |--wsgi.py
    |    |--urls.py
    |--...
    |--manage.py
    |--NameServerMngrSite.conf
    |--readme.md
    |--requirement.txt
    |--setup.sh
    |--sql.log
```
#### 安装apache和mod_wsgi
```
apt-get install apache2
apt-get install libapache2-mod-wsgi
```
#### 安装pip
```
apt-get install python-pip
```
#### 安装项目依赖
```
pip install -r NameServerMngrSite/requirement.txt
```
#### 修改目录权限
修改权限：
```
chmod -R 644 NameServerMngrSite
find NameServerMngrSite -type d | xargs chmod 755
```
修改log文件权限
```
chmod 777 NameServerMngrSite/sql.log
```
#### 配置apache站点配置文件
将下面站点文件保存为NameServerMngrSite.conf放到/etc/apache2/sites-available文件夹下，其中projectPath替换为项目路径，默认端口为80
```
<VirtualHost *:80>
    Alias /static/ projectPath/NameServerMngrSite/collected_static/

    <Directory projectPath/NameServerMngrSite/collected_static>
   Allow from all
    </Directory>

    WSGIScriptAlias / projectPath/NameServerMngrSite/NameServerMngrSite/wsgi.py

    <Directory projectPath/NameServerMngrSite/NameServerMngrSite>
    <Files wsgi.py>
   Order deny,allow
   Allow from all
    </Files>
    </Directory>
</VirtualHost>
```
#### 收集静态资源
```
python NameServerMngrSite/manage.py collectstatic
```
#### 启动服务
禁用apache默认站点
```
a2dissite default
```
启用站点
```
a2ensite NameServerMngrSite.conf
```
重启apache
```
service apache2 reload
service apache2 restart
```

### 参考

[官方文档(部署)](https://docs.djangoproject.com/en/1.11/howto/deployment/)

[教程](http://code.ziqiangxuetang.com/django/django-deploy.html)

[修改端口](http://blog.csdn.net/sunxingzhesunjinbiao/article/details/19491029)


