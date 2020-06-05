FROM arm32v7/python:3.8-alpine

WORKDIR /cucumber
COPY requirements.txt .
RUN apk add --no-cache --upgrade bash && pip install -r requirements.txt

ENV FLASK_APP webapp