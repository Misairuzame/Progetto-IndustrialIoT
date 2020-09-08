#!/bin/bash

curl -X DELETE "localhost:9200/telemetry"
curl -X DELETE "localhost:9200/clientinfo"
curl -X DELETE "localhost:9200/elaboration"