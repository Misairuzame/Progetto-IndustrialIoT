#!/bin/bash

/opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka-broker:9092 --topic telemetry --from-beginning
/opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka-broker:9092 --topic clientinfo --from-beginning
