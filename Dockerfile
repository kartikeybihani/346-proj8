FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    apache2 \
    apache2-utils \
    libapache2-mod-wsgi-py3 \
    sqlite3 \
    && apt-get clean

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
COPY gcp_creds.json /gcp_creds.json

RUN a2enmod cgi

RUN mkdir -p /var/www/cgi-bin

# Copy CGI scripts
COPY ./cgi-bin /var/www/cgi-bin

# Make CGI scripts executable
RUN chmod +x /var/www/cgi-bin/*.cgi

# Copy + run DB init
COPY ./init_db.py /init_db.py
RUN python3 /init_db.py && chmod 666 /tmp/servers.db


# ✅ MAKE DB WRITABLE
RUN chmod 666 /tmp/servers.db

# Apache config
COPY ./apache-config.conf /etc/apache2/sites-available/000-default.conf

EXPOSE 80

CMD ["apachectl", "-D", "FOREGROUND"]
