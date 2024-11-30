# 自助打印系统
## 简介
这是一个让你的打印机变成自助上传文件的打印机的系统

## 特性
- 用户端可在手机端通过扫码使用网页APP上传文件并选择打印属性并付款
- 支持接入支付宝当面付
- 商家后台（WIP）

## 搭建

### 前置需求
- 一台支持linux系统的打印机
- Windows服务器(系统最低要求windows sever 2008) 
- X86小主机或arm机顶盒或树莓派等
- 如果Windows服务器在中国且不想备案，可以多准备一台境外的服务器(可选)
- 开通支付宝当面付(请自行查找开通)
- 
### 搭建
安装Windows Office软件

Windows服务器上安装Python，版本必需3.8以及以上

`https://www.python.org/downloads/`

如果使用windows server 2008，由于Python停止了Windows sever 2008的支持，所以推荐你使用非官方支持的版本(可选)

`https://github.com/adang1345/PythonWin7`

安装Nginx

`https://nginx.org/en/download.html`

使用zerossl申请HTTPS证书，如果你的服务器在国内不想备案，请申请ip证书

`https://zerossl.com/`

在nginx目录里，找到 `conf\nginx` 添加以下配置

```
    server {
        listen       8000 ssl;
        server_name  localhost;

        ssl_certificate      C:/Users/Administrator/Desktop/nginx-1.24.0/certification.crt; #你的证书目录
        ssl_certificate_key  C:/Users/Administrator/Desktop/nginx-1.24.0/private.key; #同上
        #access_log  logs/host.access.log  main;
        location / {
        proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_pass http://127.0.0.1:8000;
			client_max_body_size 100m;
        }
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }
    }
```

用PowerShell，打开Nginx

然后将本项目文件上传至windows server，右键使用管理员身份运行start.bat

后端搭建至此，接下来内容是前端的搭建，如果没有备案，请跳转至前端非备案服务器搭建步骤

#### 前端搭建

在nginx目录里找到 `conf\nginx.conf` ，并添加以下配置

```
    server {
        listen       443 ssl;
        server_name  xxx.yyy.top; # 你的域名
		
        ssl_certificate      C:/Users/Administrator/Desktop/nginx-1.24.0/certification.crt; # HTTPS证书
        ssl_certificate_key  C:/Users/Administrator/Desktop/nginx-1.24.0/private.key; #同上
        location / {
			root  C:/Users/Administrator/Desktop/nginx-1.24.0/dist/; # 前端目录地址
        }
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }
    }
```

清除nginx进程并再次启动nginx
### 前端搭建(非备案服务器搭建，可选)

这里以Debian/Ubuntu为例子

安装nginx

`apt install nginx`

申请证书，请参考acme.sh用法

`https://github.com/acmesh-official/acme.sh/wiki/%E8%AF%B4%E6%98%8E`

克隆

`git clone https://github.com/233kun/self-service-printer`

移动前端文件

`mv self-service-printer/front/dist/* /var/www/printer`

设置文件权限

`chmod 755 -R /var/www/printer` `chown www:www`

新建nginx vhost配置文件

`nano /etc/nginx/conf.d/printer.conf`

```
server {
        listen 443 ssl;
        listen [::]:443 ssl;

        server_name printer.xxxxx.com; #你的域名
        ssl_certificate  /opt/temp.cer;  #你的证书目录
        ssl_certificate_key /opt/temp.key; #同上

        # logging
        access_log /var/log/nginx/printer.access.log;
        error_log /var/log/nginx/printer.top.error.log warn;

        # index.html fallback
        location / {
        try_files $uri $uri/ /index.html;
        root /var/www/printer;
        }
        types {
            application/javascript js mjs;
        }
    }
```
### 打印机端搭建

这里以Debian/Ubuntu/Armbian为例

首先找到你的打印机型号对应的驱动安装，这里以惠普的打印机为例

安装惠普打印机驱动(Arm架构也可用)，CUPS，Python

`sudo apt install hplip cups python3`

git克隆

`git clone https://github.com/233kun/self-service-printer`

按照注释修改配置变量

`nano client/main.py`

运行

`cd self-service-printer/client/`
`python3 main.py &`

### misc

- 已知惠普的打印机对Linux支持程度最好，并且有Arm的驱动支持，可以使用树莓派或是刷了Armbian的机顶盒这些低功耗低成本的硬件，详细请看以下网址


`https://developers.hp.com/hp-linux-imaging-and-printing/supported_devices/index`

- 理论上支持 IPP 协议的打印机都可以使用树莓配或Armbian机顶盒

### 支持我

使用我的返利链接购买阿里云，推荐购买ECS 经济型e实例，2核2G，并且可以免费使用windows server

`https://www.aliyun.com/minisite/goods?userCode=vstpu3uf`

### License

MIT License

Copyright (c) 2024 233kun

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

