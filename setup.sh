#!/bin/bash -e

# 安装apache2
apt-get install apache2
# 安装mod_wsgi
apt-get install libapache2-mod-wsgi
# 安装pip
apt-get install python-pip


# 安装依赖
pip freeze > requirement.txt
pip install -r requirement.txt


# 修改目录权限
cd ..
chmod -R 644 NameServerMngrSite
find NameServerMngrSite -type d | xargs chmod 755
# 修改log权限
cd NameServerMngrSite
chmod 777 sql.log

# 修改配置文件中的路径
curDir="$(cd `dirname $0`; pwd)"
sed -i "s:~:$curDir:g" NameServerMngrSite.conf

# 拷贝apache站点配置文件
cp NameServerMngrSite.conf /etc/apache2/sites-available/NameServerMngrSite.conf

# 收集静态资源
python manage.py collectstatic

# 禁用apache默认站点
a2dissite default
# 启用站点
a2ensite NameServerMngrSite.conf

service apache2 reload

# 重启apache
service apache2 restart
