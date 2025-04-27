#!/bin/sh

/opt/kafka/bin/kafka-topics.sh --create --topic telemetry --bootstrap-server kafka-broker:9092
/opt/kafka/bin/kafka-topics.sh --create --topic clientinfo --bootstrap-server kafka-broker:9092
