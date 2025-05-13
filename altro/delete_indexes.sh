#!/bin/bash

curl -X DELETE "localhost:9200/telemetry"
echo ""

curl -X DELETE "localhost:9200/clientinfo"
echo ""

curl -X DELETE "localhost:9200/elaboration"
echo ""
