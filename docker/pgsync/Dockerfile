FROM python:3.10

RUN mkdir /home/app
WORKDIR /home/app

COPY ./configs/pgsync/schema.json /home/app

RUN pip install pgsync