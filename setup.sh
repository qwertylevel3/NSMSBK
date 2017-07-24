#!/bin/bash -e

apt-get install apache2
apt-get install libapache2-mod-wsgi

pip install django
pip install pymysql
pip install pytz

cd ..
chmod -R 644 RuleManager
find RuleManager -type d | xargs chmod 755
cd RuleManager
chmod 777 sql.log
cp RuleManager.conf /etc/apache2/sites-available/RuleManager.conf

rm -rf ./collected_static
python manage.py collectstatic

a2dissite default
a2ensite RuleManager.conf

service apache2 restart

