#!/bin/bash

sed "s|SERVER_HOST = ''|SERVER_HOST = '$SERVER_HOST'|" setting.py.bak >setting.py
sed -i "s|PRINTER_URL = ''|PRINTER_URL = '$PRINTER_URL'|" setting.py
sed -i "s|SECRET_KEY = ''|SECRET_KEY = '$SECRET_KEY'|" setting.py

/usr/sbin/cupsd -f &
if [[ -n "$PRINTER_URL" ]]; then
  python3 main.py &
fi

wait
