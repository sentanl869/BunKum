#!/usr/bin/env bash
set -ex

until nc -nz mysql 3306 ; do
  >&2 echo "[ *** Notice *** ]: mysql is unavailable - retrying"
  sleep 3
done

cd /var/www/BunKum

python3 reset_app.py
export FLASK_APP=service.py
flask deploy