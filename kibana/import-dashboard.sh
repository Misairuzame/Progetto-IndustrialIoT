#!/bin/bash

#curl \
# --request POST 'http://localhost:5601/api/dashboards/dashboard/7bead970-f1fd-11ea-97ce-330e78d95f8e' \
# --header "Authorization: $API_KEY" \
# --header "Content-Type: application/json" \
# --header "kbn-xsrf: true" \
# --data @kibana-dashboard.json


curl -X POST "http://localhost:5601/api/saved_objects/_import?overwrite=true" \
  -H "kbn-xsrf: true" \
  -F "file=@./kibana-dashboard.ndjson"


#curl -X POST "http://localhost:5601/api/saved_objects/_log_legacy_import?overwrite=true" \
#  -H "kbn-xsrf: true" \
#  -F "file=@./kibana-dashboard.json"

#curl -X POST "http://localhost:5601/api/saved_objects/_bulk_create" \
#  -H "kbn-xsrf: true" \
#  -F "file=@./kibana-dashboard.json"
