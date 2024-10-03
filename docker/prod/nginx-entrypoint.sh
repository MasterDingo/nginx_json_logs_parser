#!/bin/sh

if [ -f /etc/ssl/certs/$SSL_CERTIFICATE -a -f /etc/ssl/private/$SSL_CERTIFICATE_KEY ]
then
    cat <<EOF > /etc/nginx/includes/https.conf
listen 443 ssl;
ssl_certificate /etc/ssl/certs/${SSL_CERTIFICATE};
ssl_certificate_key /etc/ssl/private/${SSL_CERTIFICATE_KEY};
EOF
else
    echo "listen 80;" > /etc/nginx/includes/http.conf
fi