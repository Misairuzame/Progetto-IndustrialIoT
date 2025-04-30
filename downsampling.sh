#!/bin/bash

curl -s -X POST http://localhost:9200/_transform/_preview -H "Content-Type: application/json" -d '{
  "source": {
    "index": "telemetry"
  },
  "dest": {
    "index": "elaboration_downsampled"
  },
  "pivot": {
    "group_by": {
      "clientid": {
        "terms": {
          "field": "clientid"
        }
      },
      "timestamp_histogram": {
        "date_histogram": {
          "field": "@timestamp",
          "fixed_interval": "15m"
        }
      }
    },
    "aggregations": {
      "avg_telemetry_panels_total": {
        "avg": {
          "field": "telemetry.panels.total"
        }
      },
      "max_telemetry_panels_total": {
        "max": {
          "field": "telemetry.panels.total"
        }
      },
      "sum_telemetry_panels_total": {
        "sum": {
          "field": "telemetry.panels.total"
        }
      },
      "min_telemetry_consumption_grid": {
        "min": {
          "field": "telemetry.elmeter.consumption-grid"
        }
      },
      "max_telemetry_consumption_grid": {
        "max": {
          "field": "telemetry.elmeter.consumption-grid"
        }
      },
      "sum_telemetry_consumption_grid": {
        "sum": {
          "field": "telemetry.elmeter.consumption-grid"
        }
      },
      "max_telemetry_feeding": {
        "max": {
          "field": "telemetry.elmeter.feeding"
        }
      },
      "sum_telemetry_feeding": {
        "sum": {
          "field": "telemetry.elmeter.feeding"
        }
      }
    }
  }
}'
