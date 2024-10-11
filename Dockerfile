
ARG NGINX_VERSION=1.18.0
ARG CRS_VERSION=4.7.0

FROM debian:bullseye-slim

ARG NGINX_VERSION
ARG CRS_VERSION

RUN apt-get update && apt-get install -y \
    build-essential \
    libpcre3 libpcre3-dev \
    zlib1g zlib1g-dev \
    libssl-dev \
    wget \
    git \
    curl \
    unzip \
    libmaxminddb-dev \
    libyajl-dev \
    pkg-config \
    liblmdb-dev \
    doxygen \
    libtool \
    autoconf \
    automake \
    apache2-dev \
    nginx \
    python3-pip

RUN pip3 install Flask requests


RUN wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz && \
    tar zxvf nginx-${NGINX_VERSION}.tar.gz

RUN git clone --recursive https://github.com/owasp-modsecurity/ModSecurity ModSecurity && \
    cd ModSecurity && \
    ./build.sh && \
    ./configure && \
    make install

RUN git clone --depth 1 https://github.com/owasp-modsecurity/ModSecurity-nginx.git /modsecurity-nginx

RUN cd nginx-${NGINX_VERSION} && \
    ./configure --with-compat --add-dynamic-module=../modsecurity-nginx && \
    make && make install

RUN mkdir -p /usr/share/nginx/modules/ && \
    cp /nginx-${NGINX_VERSION}/objs/ngx_http_modsecurity_module.so /usr/share/nginx/modules/ && \
    mkdir -p /etc/nginx/modsec



RUN curl -L https://github.com/coreruleset/coreruleset/archive/refs/tags/v${CRS_VERSION}.zip -o /tmp/crs.zip && \
    unzip /tmp/crs.zip -d /tmp/ && \
    cp /tmp/coreruleset-${CRS_VERSION}/crs-setup.conf.example /etc/nginx/modsec/crs-setup.conf && \
    cp -r /tmp/coreruleset-${CRS_VERSION}/rules /etc/nginx/modsec/


COPY modsecurity.conf /etc/nginx/modsec/modsecurity.conf
COPY nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p /var/log/modsecurity && \
    touch /var/log/modsecurity/debug.log && \
    chown -R www-data:www-data /var/log/modsecurity && \
    chmod -R 755 /var/log/modsecurity

COPY api.py /usr/src/app/api.py
COPY server.py /usr/src/app/server.py
CMD ["sh", "-c", "python3 /usr/src/app/api.py & python3 /usr/src/app/server.py & nginx -g 'daemon off;'"]
