FROM python:3.7.8-slim

COPY requirements.txt requirements.txt
RUN pip install -U pip && pip install -r requirements.txt

COPY ./v1 /app/v1
COPY ./bin /app/bin
COPY sqlite_setup.sql /app/sqlite_setup.sql
WORKDIR /app

RUN useradd demo
USER demo

EXPOSE 8080

ENTRYPOINT ["bash", "/app/bin/setup.sh"]