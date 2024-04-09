FROM python:3.11.9-alpine

# For performance
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# expose app to docker
ENV FLASK_APP=app.py

# Önce gerekenleri indiriyor sonra yer kaplaması diye siliyor çoğu mysql kurulumu için gerekli
RUN apk add --no-cache mariadb-connector-c-dev && \
    apk add --no-cache --virtual .build-deps mariadb-dev gcc musl-dev && \
    pip install mysqlclient && \
    apk del .build-deps

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .