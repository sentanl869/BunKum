FROM ubuntu:18.04

RUN mkdir -p /root/.pip \
    && mkdir -p /var/www/BunKum

WORKDIR /var/www/BunKum

COPY . $WORKDIR

EXPOSE 3000

RUN cp /var/www/BunKum/docker/misc/sources.list /etc/apt/sources.list \
    && cp /var/www/BunKum/docker/misc/pip.conf /root/.pip/pip.conf \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends python3 python3-pip supervisor locales netcat \
    && echo "LC_ALL=en_US.UTF-8" >> /etc/environment \
    && echo "LANG=en_US.UTF-8" >> /etc/environment \
    && echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
    && echo "LANG=en_US.UTF-8" > /etc/locale.conf \
    && locale-gen en_US.UTF-8 \
    && python3 -m pip install --no-cache-dir -U pip \
    && python3 -m pip install --no-cache-dir gunicorn gevent psutil wheel\
    && python3 -m pip install --no-cache-dir -r requirements.txt \
    && python3 -m pip uninstall -y wheel \
    && apt-get remove -y python3-pip \
    && apt-get purge -y --auto-remove python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && cp /var/www/BunKum/docker/misc/blog.conf /etc/supervisor/conf.d/blog.conf \
    && cp /var/www/BunKum/docker/misc/celery.conf /etc/supervisor/conf.d/celery.conf \
    && chmod -R o+rwx /var/www/BunKum

ENV LANG=en_US.utf-8 \
    LC_ALL=en_US.utf-8

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
