#!/usr/bin/env bash
set -ex

apt-get install -y ufw
ufw allow 22
ufw allow 80
ufw allow 443
ufw allow 465
ufw default deny incoming
ufw default allow outgoing
ufw status verbose
ufw -f enable

apt-get install -y supervisor nginx python3-pip mysql-server redis-server

mysql -u root -e "DELETE FROM mysql.user WHERE User='';"
mysql -u root -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
mysql -u root -e "DROP DATABASE IF EXISTS test;"
mysql -u root -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"

mysql_password=$(awk -F '[=\r]' 'NR==1 {print $2}' /var/www/BunKum/.env)
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$mysql_password';"

rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-available/default

cp /var/www/BunKum/misc/blog.conf /etc/supervisor/conf.d/blog.conf
cp /var/www/BunKum/misc/celery.conf /etc/supervisor/conf.d/celery.conf
cp /var/www/BunKum/misc/blog.nginx /etc/nginx/sites-enabled/blog

chmod -R o+rwx /var/www/BunKum

cd /var/www/BunKum
python3 -m pip install -U pip
python3 -m pip install gunicorn gevent psutil
python3 -m pip install -r requirements.txt
service mysql restart
python3 reset_app.py
export FLASK_APP=service.py
flask deploy

service supervisor restart
service nginx restart

hostname -I