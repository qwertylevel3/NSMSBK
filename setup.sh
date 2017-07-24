#!/bin/bash -e

# 安装apache2
apt-get install apache2
# 安装mod_wsgi
apt-get install libapache2-mod-wsgi


# 安装依赖
pip freeze > requirement.txt
pip install -r requirement.txt


# 修改目录权限
cd ..
chmod -R 644 RuleManager
find RuleManager -type d | xargs chmod 755
# 修改log权限
cd RuleManager
chmod 777 sql.log

# 拷贝apache站点配置文件
cp RuleManager.conf /etc/apache2/sites-available/RuleManager.conf

# 收集静态资源
rm -rf ./collected_static
python manage.py collectstatic

# 禁用apache默认站点
a2dissite default
# 启用站点
a2ensite RuleManager.conf

# 重启apache
service apache2 restart
