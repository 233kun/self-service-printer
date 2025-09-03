FROM caddy:latest

ENV BASEURL=""
ENV TITLE=""
ENV PRICE=""
ENV DISCOUNTEDPRICE=""
ENV DOMAIN=""
ENV EMAIL=""

COPY Caddyfile.bak /etc/caddy/Caddyfile.bak
COPY start.sh /src/start.sh
COPY dist /src/dist

WORKDIR /src

RUN chmod +x start.sh

CMD "./start.sh"
