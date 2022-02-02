FROM python:alpine
# using python 3.10

LABEL maintainer="art.goldhammer@gmail.com"

# substituting gunicorn for uwsgi
RUN apk add --update --no-cache \
    # uwsgi-python3 \
    logrotate \
    supervisor

# RUN python3 -m ensurepip
RUN pip3 install --upgrade pip
# RUN pip install wheel


RUN mkdir /nooze; mkdir -p /var/log/nooze
RUN touch /var/log/nooze/nooze.log

RUN mkdir -p /var/log/uwsgi
RUN touch /var/log/uwsgi/uwsgi.log
RUN mkdir /app

# install the standing requirements
COPY requirements.txt /nooze
RUN pip install -r /nooze/requirements.txt
RUN pip install gunicorn

# install the app environment
COPY nzdb/ /nooze/nzdb/
# RUN ls -laR /nooze
COPY setup.py /nooze
WORKDIR /nooze
# RUN ls -laR /nooze
# RUN python3 setup.py install
# leave installation editable for now
RUN pip install -e .
# RUN rm -rf /nooze
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
# ENTRYPOINT ["supervisord", "-n"]

