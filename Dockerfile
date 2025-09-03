FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractivea
ENV SECRET_KEY=""
ENV APP_ID=""
ENV ALIPAY_PUBLIC_KEY=""
ENV ALIPAY_PRIVATE_KEY=""
ENV SERVER_HOST=""
ENV CONVERT_TOOL=""
ENV DOMAIN=""
ENV EMAIL=""
ENV ACCEPT_WPS_EULA=""
ENV VNC_PASSWORD="password"

RUN apt-get update && apt-get install -y \
  lxqt x11vnc xvfb dbus-x11 supervisor\
  curl git \
  python3 python3-pip caddy \
  libtiff6 \
  && apt-get clean && rm -rf /var/lib/apt/lists/* \
  && ln -sv /usr/lib/x86_64-linux-gnu/libtiff.so.6 /usr/lib/x86_64-linux-gnu/libtiff.so.5 \
  && ldconfig

WORKDIR /opt
RUN git clone https://github.com/novnc/noVNC /opt/noVNC \
  && git clone https://github.com/novnc/websockify /opt/websockify \
  && chmod +x /opt/websockify/run \
  && ln -s /opt/noVNC/vnc_lite.html /opt/noVNC/index.html \
  && curl -LJO https://github.com/Rongronggg9/wps-office-repack/releases/download/v11.1.0.11723/wps-office_11.1.0.11723_amd64.deb \
  && dpkg -i wps-office_11.1.0.11723_amd64.deb \
  && git clone https://github.com/dv-anomaly/ttf-wps-fonts.git \
  && cd ttf-wps-fonts \
  && bash install.sh \
  && rm -rf /opt/ttf-wps-fonts \
  && rm /opt/wps-office_11.1.0.11723_amd64.deb


COPY supervisord.conf /etc/supervisor/conf.d/vnc.conf

RUN useradd -m docker && echo "docker:docker" | chpasswd && adduser docker sudo
WORKDIR /home/docker
COPY . .
RUN pip install -r requirements.txt --break-system-packages


RUN mv ./Caddyfile.bak /etc/caddy/ && mv supervisord.conf /etc/supervisor/conf.d/vnc.conf
RUN chmod +x start.sh
CMD "./start.sh"
