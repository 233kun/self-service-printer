#!/bin/bash

check_empty_env() {
  local empty_vars=()

  [[ -z "$SERVER_HOST" ]] && empty_vars+=("SERVER_HOST")
  [[ -z "$PRINTER_URL" ]] && empty_vars+=("PRINTER_URL")
  [[ -z "$SECRET_KEY" ]] && empty_vars+=("SECRET_KEY")
  if [ ${#empty_vars[@]} -gt 0 ]; then
    echo "警告: 以下必需的环境变量为空或未设置:"
    for var in "${empty_vars[@]}"; do
      echo "  - $var"
    done
    echo "请设置以上环境变量后再运行Docker"
  fi
}

check_empty_env

sed "s|SERVER_HOST = ''|SERVER_HOST = '$SERVER_HOST'|" setting.py.bak >setting.py
sed -i "s|PRINTER_URL = ''|PRINTER_URL = '$PRINTER_URL'|" setting.py
sed -i "s|SECRET_KEY = ''|SECRET_KEY = '$SECRET_KEY'|" setting.py

/usr/sbin/cupsd -f &
if [[ -n "$PRINTER_URL" ]]; then
  python3 main.py &
fi

wait
