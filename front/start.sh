#!/bin/sh

check_empty_env() {
  empty_vars=""

  [ -z "$BASEURL" ] && empty_vars="$empty_vars BASEURL"
  [ -z "$PRICE" ] && empty_vars="$empty_vars PRICE"
  [ -z "$DISCOUNTEDPRICE" ] && empty_vars="$empty_vars DISCOUNTEDPRICE"

  if [ -n "$empty_vars" ]; then
    echo "警告: 以下必需的环境变量为空或未设置:" >&2
    for var in $empty_vars; do
      echo "  - $var" >&2
    done
    echo "请设置以上环境变量后再运行Docker" >&2
  fi
}
check_empty_env

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
  sed -i "s|TLS||" /etc/caddy/Caddyfile.bak
  mv /etc/caddy/Caddyfile.bak /etc/caddy/Caddyfile
else
  echo "警告:HTTPS未正确配置"
fi

caddy run --config /etc/caddy/Caddyfile
