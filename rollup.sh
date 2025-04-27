#!/bin/bash

curl -X PUT "localhost:9200/_rollup/job/rolltele" -H "Content-type: application/json" -d '
{
	"index_pattern": "test4",
	"rollup_index": "elaboration",
	"cron": "*/30 * * * * ?",
	"page_size": 1000,
	"groups": {
    "date_histogram": {
      "field": "@timestamp",
      "fixed_interval": "15m"
    },
    "terms": {
    	"fields": [ "clientid" ]
    }
  },
  "metrics": [
  	{
  		"field": "telemetry.panels.total",
  		"metrics": [ "avg", "max", "sum" ]
  	},
  	{
  		"field": "telemetry.elmeter.consumption-grid",
  		"metrics": [ "min", "max", "sum" ]
  	},
  	{
  		"field": "telemetry.elmeter.feeding",
  		"metrics": [ "max", "sum" ]
  	}
  ]
}'
