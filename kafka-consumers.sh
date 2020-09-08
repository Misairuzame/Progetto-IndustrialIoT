#!/bin/bash

gnome-terminal -t "Topic 'telemetry'" --tab -- /usr/local/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic telemetry --from-beginning
gnome-terminal -t "Topic 'clientinfo'"  --tab -- /usr/local/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic clientinfo --from-beginning
