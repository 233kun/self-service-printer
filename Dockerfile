FROM python:3-slim

RUN apt update
RUN apt install -y curl bsdmainutils xdg-utils libxslt1.1 xvfb libqt5gui5 libglu1-mesa
# get the download URL from https://aur.archlinux.org/packages/wps-office
RUN curl -O https://wdl1.pcfg.cache.wpscdn.com/wpsdl/wpsoffice/download/linux/11723/wps-office_11.1.0.11723.XA_amd64.deb
RUN dpkg -i wps-office_11.1.0.11723.XA_amd64.deb

WORKDIR /usr/src/self-service-printer-backend

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]