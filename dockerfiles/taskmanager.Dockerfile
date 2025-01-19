FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Sao_Paulo

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update
RUN apt install -y python3.11 python3.11-dev python3-pip
RUN apt install -y libpq-dev
RUN apt install -y poppler-utils

WORKDIR /usr/src/app

COPY api/requirements.txt requirements.txt
COPY taskmanager/ taskmanager/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 80

SHELL [ "/bin/bash", "-c"]

CMD "celery" "-A" "taskmanager.beat" "beat" "--loglevel" "DEBUG"
