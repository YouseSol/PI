FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Sao_Paulo

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update
RUN apt install -y python3.11 python3.11-dev python3-pip
RUN apt install -y libpq-dev

WORKDIR /usr/src/app

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

COPY api api
COPY api/requirements.txt requirements.txt

RUN python3.11 -m pip install --upgrade pip
RUN python3.11 -m pip install -r requirements.txt

SHELL [ "/bin/bash", "-c" ]

ENTRYPOINT [ "/entrypoint.sh" ]
