#!/bin/sh

KIBANA_ADDRESS="kibana:5601"

# Import Kibana Dashboard
curl -s -X POST "http://${KIBANA_ADDRESS}/api/saved_objects/_import?overwrite=true" \
  -H "kbn-xsrf: true" \
  -F "file=@./kibana-dashboard.ndjson"
