FROM olbat/cupsd

ENV SERVER_HOST=""
ENV PRINTER_URL=""
ENV SECRET_KEY=""

RUN apt-get update && apt-get install -y python3

COPY . .
RUN chmod +x start.sh

CMD "./start.sh"
