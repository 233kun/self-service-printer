#!/bin/sh

sed "s|baseURL: ''|baseURL: '$BASEURL'|" dist/static/config.js.bak >dist/static/config.js.tmp
sed -i "s|price: |price: $PRICE|" dist/static/config.js.tmp
sed -i "s|discountedPrice: |discountedPrice: $DISCOUNTEDPRICE|" dist/static/config.js.tmp
mv dist/static/config.js.tmp dist/static/config.js

crt_file=$(ls /etc/caddy/*.crt 2>/dev/null)
key_file=$(ls /etc/caddy/*.key 2>/dev/null)
if [ -n "$crt_file" ] && [ -n "$key_file" ]; then
  sed -i "s|DOMAIN|$DOMAIN|" /etc/caddy/Caddyfile.bak
  sed -i "s|TLS|tls $crt_file $key_file|" /etc/caddy/Caddyfile.bak
  mv /etc/caddy/Caddyfile.bak /etc/caddy/Caddyfile
elif [ -n "$EMAIL" ]; then
  sed -i "s|DOMAIN|$DOMAIN|" /etc/caddy/Caddyfile.bak
  sed -i "s|TLS|tls $EMAIL|" /etc/caddy/Caddyfile.bak
  mv /etc/caddy/Caddyfile.bak /etc/caddy/Caddyfile
fi

#cat dist/static/config.js
#cat /etc/caddy/Caddyfile
caddy run --config /etc/caddy/Caddyfile --adapter caddyfile &
