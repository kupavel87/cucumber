FROM arm32v7/python:3.7.7-slim-buster

WORKDIR /cucumber
COPY requirements.txt .
RUN apt-get update -y && apt-get install -y libatlas-base-dev
RUN pip install --extra-index-url=https://www.piwheels.org/simple --no-cache-dir -r requirements.txt

ENV FLASK_APP webapp