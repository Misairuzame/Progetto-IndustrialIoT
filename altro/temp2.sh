#!/bin/bash

curl -X POST "localhost:9200/_search/scroll?pretty" -H 'Content-Type: application/json' -d'
{
  "scroll" : "30s",                                                                 
  "scroll_id" : "FGluY2x1ZGVfY29udGV4dF91dWlkDXF1ZXJ5QW5kRmV0Y2gBFFpuYy1aSFFCTmZGb3hmSzU2ZGdaAAAAAAAAEaAWM09PUGU5dWFSTWEtRE90RktiMUV0Zw==" 
}'
