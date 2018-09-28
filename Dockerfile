FROM alpine:3.8

MAINTAINER artgoldhammer

RUN apk add --no-cache \
	uwsgi-python3 \
    logrotate \
	python3 \
    supervisor

RUN mkdir nooze; mkdir -p /var/log/nooze
RUN touch /var/log/nooze/nooze.log

RUN mkdir -p /var/log/uwsgi
RUN touch /var/log/uwsgi/uwsgi.log
RUN mkdir /app

# install the standing requirements
COPY requirements.txt nooze/
RUN pip3 install --upgrade pip
RUN pip3 install -r nooze/requirements.txt

COPY app/ /app/
# RUN ls -laR /app

# install the app environment
COPY nzdb/ /nooze/nzdb/
# RUN ls -laR /nooze
COPY setup.py nooze/
WORKDIR nooze
RUN python3 setup.py install

# 
# RUN cp -r /nooze/app/ /
# config files should be placed in $HOME/confs dir on host
# RUN cp -r /nooze/confs /app

# 
RUN mkdir -p /etc/supervisor.d
RUN ln -s /app/supervisor.ini /etc/supervisor.d/
# 
RUN rm -rf /nooze

# CMD tail -f /dev/null
WORKDIR /app
CMD ["supervisord", "-n"]


