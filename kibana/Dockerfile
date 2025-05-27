FROM alpine

RUN apk add curl

COPY startup.sh .

COPY kibana-dashboard.ndjson dashboard.ndjson

CMD ["sh", "startup.sh"]
