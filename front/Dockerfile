FROM caddy:latest

ENV BASEURL=""
ENV PRICE=""
ENV DISCOUNTEDPRICE=""

COPY Caddyfile /etc/caddy/Caddyfile
COPY start.sh /src/start.sh
COPY dist /src/dist

WORKDIR /src

RUN chmod +x start.sh

CMD /src/start.sh
