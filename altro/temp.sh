#!/bin/bash

curl -X POST "localhost:9200/test4/_search?scroll=30s" -H "Content-type: application/json" -d '{
	"query": {
        "bool": {
			"must": [
				{
					"exists": {
						"field": "telemetry"
					}
				},
				{
					"range": {
						"telemetry.timestamp": {
							"gte": 0,
							"lte": 9999999999999999999
						}
					}
				}
			]
		}
  },
  "size": 10
}'
