FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt install -y python3.11 python3.11-dev python3-pip
RUN apt install -y libpq-dev

WORKDIR /usr/src/app

COPY appconfig appconfig
RUN python3.11 -m pip install -r appconfig/requirements.txt

COPY api/requirements.txt requirements.txt
COPY taskmanager taskmanager

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 80

SHELL [ "/bin/bash", "-c"]

CMD "celery" "-A" "taskmanager.beat" "beat" "--loglevel" "DEBUG"
