#!/bin/sh

if [ -z "$ELASTIC_ADDRESS" ]; then
    ELASTIC_ADDRESS="elasticsearch:9200"
fi
# Create Elastic indexes and set mappings.

# Before that, delete indexes if they exist!
curl -s -X DELETE "${ELASTIC_ADDRESS}/telemetry"
echo ""

curl -s -X DELETE "${ELASTIC_ADDRESS}/clientinfo"
echo ""

curl -s -X DELETE "${ELASTIC_ADDRESS}/elaboration"
echo ""

# Create indexes and mappings.
curl -s -X PUT "${ELASTIC_ADDRESS}/telemetry"
echo ""

curl -s -X PUT "${ELASTIC_ADDRESS}/clientinfo"
echo ""

curl -s -X PUT "${ELASTIC_ADDRESS}/elaboration"
echo ""

curl -s -X PUT "${ELASTIC_ADDRESS}/telemetry/_mapping" -H 'Content-Type: application/json' -d'
{
    "properties": {
        "@timestamp": { "type": "date" },
        "clientid": { "type": "keyword" },
        "telemetry.panels.p1": { "type": "float" },
        "telemetry.panels.p2": { "type": "float" },
        "telemetry.panels.p3": { "type": "float" },
        "telemetry.panels.p4": { "type": "float" },
        "telemetry.panels.p5": { "type": "float" },
        "telemetry.panels.p6": { "type": "float" },
        "telemetry.panels.p7": { "type": "float" },
        "telemetry.panels.p8": { "type": "float" },
        "telemetry.panels.p9": { "type": "float" },
        "telemetry.panels.p10": { "type": "float" },
        "telemetry.panels.p11": { "type": "float" },
        "telemetry.panels.p12": { "type": "float" },
        "telemetry.panels.p13": { "type": "float" },
        "telemetry.panels.p14": { "type": "float" },
        "telemetry.panels.p15": { "type": "float" },
        "telemetry.panels.p16": { "type": "float" },
        "telemetry.panels.p17": { "type": "float" },
        "telemetry.panels.p18": { "type": "float" },
        "telemetry.panels.p19": { "type": "float" },
        "telemetry.panels.p20": { "type": "float" },
        "telemetry.panels.total": { "type": "float" },
        "telemetry.batteries.total-charge": { "type": "float" },
        "telemetry.elmeter.consumption-grid": { "type": "float" },
        "telemetry.elmeter.feeding": { "type": "float" },
        "telemetry.elmeter.consumption-required": { "type": "float" }
    }
}
'
echo ""

curl -s -X PUT "${ELASTIC_ADDRESS}/clientinfo/_mapping" -H 'Content-Type: application/json' -d'
{
    "properties": {
        "clientinfo.clientid": { "type": "keyword" },
        "clientinfo.clientname": { "type": "text" },
        "clientinfo.position": { "type": "geo_point" }
    }
}
'
echo ""

curl -s -X PUT "${ELASTIC_ADDRESS}/elaboration/_mapping" -H 'Content-Type: application/json' -d'
{
    "properties": {
        "clientinfo.clientid": { "type": "keyword" },
        "clientinfo.clientname": { "type": "text" },
        "clientinfo.position": { "type": "geo_point" },
        "bill-timestamp": {
            "type": "date",
            "format": "epoch_second"
        },
        "period": { "type": "text" },
        "fed-into-grid": { "type": "float" },
        "consumed-grid": { "type": "float" },
        "total-house-consumed": { "type": "float" },
        "gained-feeding": { "type": "float" },
        "price-consumed": { "type": "float" },
        "total-to-pay": { "type": "float" },
        "to-be-credited": { "type": "float" }
    }
}
'
echo ""
