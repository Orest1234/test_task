FROM python:3.9-slim
COPY . /root
WORKDIR /root


RUN pip install --upgrade pip


RUN pip install flask gunicorn flask_wtf matplotlib shapely PyShp