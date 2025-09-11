#!/bin/bash

check_empty_env() {
  local empty_vars=()

  [[ -z "$SECRET_KEY" ]] && empty_vars+=("SECRET_KEY")
  [[ -z "$SERVER_HOST" ]] && empty_vars+=("SERVER_HOST")
  [[ -z "$APP_ID" ]] && empty_vars+=("APP_ID")
  [[ -z "$ALIPAY_PUBLIC_KEY" ]] && empty_vars+=("ALIPAY_PUBLIC_KEY")
  [[ -z "$ALIPAY_PRIVATE_KEY" ]] && empty_vars+=("ALIPAY_PRIVATE_KEY")
  if [ ${#empty_vars[@]} -gt 0 ]; then
    echo "警告: 以下必需的环境变量为空或未设置:"
    for var in "${empty_vars[@]}"; do
      echo "  - $var"
    done
    echo "请设置以上环境变量后再运行Docker"
  fi
}

check_empty_env

sed "s|SECRET_KEY = ''|SECRET_KEY = '$SECRET_KEY'|" setting.py.bak >setting.py.tmp
sed -i "s|SERVER_HOST = ''|SERVER_HOST = '$SECRET_HOST'|" setting.py.tmp
sed -i "s|APP_ID = ''|APP_ID = '$APP_ID'|" setting.py.tmp
sed -i "s|ALIPAY_PUBLIC_KEY = ''|ALIPAY_PUBLIC_KEY = '$ALIPAY_PUBLIC_KEY'|" setting.py.tmp
sed -i "s|ALIPAY_PRIVATE_KEY = ''|ALIPAY_PRIVATE_KEY = '$ALIPAY_PRIVATE_KEY'|" setting.py.tmp
sed -i "s|CONVERT_TOOL = ''|CONVERT_TOOL = 'WPS'|" setting.py.tmp

mv setting.py.tmp setting.py

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
else
  echo "错误：HTTPS未正确配置"
fi

if (($ACCEPT_WPS_EULA == "true")); then
  timeout 3 xvfb-run wps
  echo "common\AcceptedEULA=true" >>/root/.config/Kingsoft/Office.conf
  echo "common\UserInfo\ACUPI=true" >>/root/.config/Kingsoft/Office.conf
  echo "wpsoffice\Application%20Settings\AppComponentMode=prome_independ" >>/root/.config/Kingsoft/Office.conf
  echo "wpsoffice\Application%20Settings\AppComponentModeInstall=prome_independ" >>/root/.config/Kingsoft/Office.conf
  timeout 3 xvfb-run wps
else
  echo "请同意WPS Office用户许可协议"
  echo "https://privacy.wps.cn/policies/eula/personal-wps-office"
  exit 1
fi

sed -i "s|VNC_PASSWORD|$VNC_PASSWORD|" /etc/supervisor/conf.d/vnc.conf

/usr/bin/supervisord -n &
caddy run --config /etc/caddy/Caddyfile &
xvfb-run python3 ./main.py
