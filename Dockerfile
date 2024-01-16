#FROM python:3.8-slim-buster
FROM ubuntu:latest
WORKDIR /python-docker

RUN apt update
RUN apt-get upgrade -y
RUN apt-get install -y python3-pip python-dev-is-python3 libmysqlclient-dev
RUN apt-get install -y gcc default-libmysqlclient-dev pkg-config 
RUN rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["gunicorn"  ,"--workers=2", "-b", "0.0.0.0:8080", "app:app"]
#EXPOSE 80
#ENTRYPOINT python app.py