FROM alpine:3.8

MAINTAINER artgoldhammer

RUN apk add --no-cache \
	uwsgi-python3 \
    logrotate \
	python3 \
    supervisor

RUN mkdir app; mkdir -p /var/log/nooze

RUN touch /var/log/nooze/nooze.log

RUN mkdir nooze

COPY . /nooze

RUN cd nooze

RUN mv app /

RUN ln -s /app/supervisor.ini /etc/supervisor.ini

RUN pip3 install -r requirements.txt

RUN pip3 install . 
