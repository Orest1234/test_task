FROM alpine:latest
# Update to configure dependencies you need to solve the task
RUN apk update && apk add python3
RUN mkdir /app
WORKDIR /app
COPY main.py main.py