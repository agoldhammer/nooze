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

COPY . nooze/

# this is a kludge until tweepy is updated
# source taken from tweepy master and given new version
RUN pip3 install --upgrade pip
# RUN pip3 install nooze/tweepy-3.6.0a0.tar.gz
# 
RUN pip3 install -r nooze/requirements.txt
# 
WORKDIR nooze
RUN python setup.py install

# 
WORKDIR /
RUN cp -r /nooze/app/ /

# 
RUN ln -s /app/supervisor.ini /etc/supervisor.ini
# 
RUN rm -rf nooze

