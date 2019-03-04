FROM python:2.7-alpine

RUN apk add --no-cache build-base \
  && pip install twisted \
  && apk del build-base

EXPOSE 8080

COPY python/ /tmp

ENTRYPOINT ["python", "/tmp/main.py"]