FROM python:3.10

ENV PYTHONUNBUFFERED 1

RUN mkdir /home/app
WORKDIR /home/app

# Install system requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./app /home/app