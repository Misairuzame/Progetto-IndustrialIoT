FROM alpine

RUN apk add curl

COPY startup.sh kibana-dashboard.ndjson ./

CMD ["sh", "startup.sh"]
