FROM python:2
MAINTAINER Nicholas Herriot

WORKDIR /app
ADD ras-party ./ras-party
ADD requirements.txt ./

RUN pip install -r requirements.txt

ENTRYPOINT python ras-party/app.py
