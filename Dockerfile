FROM python:3.8.3-alpine

WORKDIR /cucumber
COPY . .
RUN pip install -r requirements.txt && chmod +x run.sh

ENV FLASK_APP webapp