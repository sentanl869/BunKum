#!/usr/bin/env bash
set -ex

cp /var/www/BunKum/misc/sources.list /etc/apt/sources.list
mkdir -p /root/.pip
cp /var/www/BunKum/misc/pip.conf /root/.pip/pip.conf
apt-get update