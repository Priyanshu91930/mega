FROM alpine:latest

RUN apk update && apk upgrade
RUN apk add --no-cache gcc python3-dev musl-dev linux-headers git py3-pip ffmpeg coreutils
RUN apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ megatools

WORKDIR /app/
COPY . .
RUN python3 -m venv venv
RUN venv/bin/pip install -U -r requirements.txt

# Disable Python output buffering so logs appear in docker logs immediately
ENV PYTHONUNBUFFERED=1

CMD ["venv/bin/python3", "-u", "-m", "megadl"]