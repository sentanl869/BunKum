#!/usr/bin/env bash
set -ex

until nc -z mysql 3306; do
  sleep 3
done

cd /var/www/BunKum

python3 reset_app.py

export FLASK_APP=service.py

flask deploy