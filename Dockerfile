FROM alpine:3.10.3

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

# install the app environment
COPY nzdb/ /nooze/nzdb/
# RUN ls -laR /nooze
COPY setup.py nooze/
WORKDIR nooze
RUN python3 setup.py install
RUN rm -rf /nooze
# 
RUN mkdir -p /etc/supervisor.d
RUN ln -s /app/supervisor.ini /etc/supervisor.d/
# 

# CMD tail -f /dev/null
COPY app/ /app/
WORKDIR /app
RUN cp /app/logging/*conf /etc/logrotate.d
RUN chmod 644 /etc/logrotate.d/*.conf
# RUN chown root:root /etc/logrotate.d/*conf
RUN chmod 755 /var/log/uwsgi
RUN chmod 755 /var/log/nooze
# the following line is necessary to make logrotate run w/o hiccup
RUN touch /var/log/messages
#
ENTRYPOINT ["supervisord", "-n"]

