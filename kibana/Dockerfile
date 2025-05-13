FROM alpine

RUN apk add curl

COPY startup.sh .

COPY dashboard-new.ndjson dashboard.ndjson

CMD ["sh", "startup.sh"]
