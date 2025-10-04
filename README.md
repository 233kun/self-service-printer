# 自助印

## 简介

一个让你的打印机变成自助上传文件的打印机的项目

## 特性

- 用户端可在手机端通过扫码使用网页APP上传文件并选择打印属性并付款
- 支持接入支付宝当面付

## 搭建

### 前置需求

- 一台支持网络打印的打印机（参考 <https://www.pwg.org/printers> ）
- 运行内存2G及以上的云服务器
- 域名  
- 开通支付宝当面付(请自行查找开通)

### 使用Docker Compose部署前后端（推荐）

⚠️ 如果你的服务器在中国，如果不想备案，可以申请IP SSL证书，并自行修改 docker-compose.yml 和 Caddyfile

#### 安装Docker和Docker-Compose

`sudo apt update && sudo apt install -y docker.io docker-compose`

#### 拉取docker-compose

`git clone https://github.com/233kun/self-service-printer`
`cd self-service-printer/docker-compose`

#### 根据注释修改参数

`nano docker-compose.yml`

#### 启动Docker

`sudo docker-compose up -d`

### 使用Docker Compose部署打印机端（推荐）

#### 安装Docker, Docker-compose, 拉取配置文件

`sudo apt update && sudo apt install -y docker.io docker-compose`
`git clone https://github.com/233kun/self-service-printer`
`cd self-service-printer/docker-compose/client`

#### 根据注释修改参数并启动

⚠️ 如果你使用的打印机不支持网络打印仅USB打印，请查看 `https://hub.docker.com/r/olbat/cupsd` 修改docker-compose.yml文件或手动部署

请在第一次启动后在浏览器访问 `http://127.0.0.1:631` 在CUPS管理页面添加你的打印机，默认管理员用户密码`print/print`

`sudo docker-compose up -d`

添加打印机后，访问 `http://localhost:631/printers/` ，找到你刚才的打印机，保存你刚才添加的打印机的URL，然后根据注释修改参数

`nano docker-compose.yml`

再次启动

`sudo docker-compose up -d`

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
