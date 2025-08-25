#!/bin/bash

sed "s|SECRET_KEY = ''|SECRET_KEY = |'$SECRET_KEY'" start.sh >start.sh.tmp
sed -i "s|SERVER_HOST = ''|SERVER_HOST = |'$SECRET_KEY'" start.sh.tmp
sed -i "s|APP_ID = ''|APP_ID = '$APP_ID'|" start.sh.tmp
sed -i "s|ALIPAY_PUBLIC_KEY = ''|ALIPAY_PUBLIC_KEY = '$ALIPAY_PUBLIC_KEY'|" start.sh.tmp
sed -i "s|ALIPAY_PRIVATE_KEY = ''|ALIPAY_PRIVATE_KEY = ''|" start.sh.tmp
sed -i "s|CONVERT_TOOL = ''|CONVERT_TOOL = '$CONVERT_TOOL'|" start.sh.tmp

mv start.sh.tmp start.sh

python ./main.py
