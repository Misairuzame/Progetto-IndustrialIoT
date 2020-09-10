#!/bin/bash

#gnome-terminal -t "Mosquitto" --tab -- sh mosquitto-start.sh
#echo "Sleeping 15s... Mosquitto starting"
#sleep 15

#gnome-terminal -t "Kafka Consumers" --tab -- sh kafka-consumers.sh
#sleep 3
#echo "Kafka consumers starting"

gnome-terminal -t "Filebeat" --tab -- sh filebeat-start.sh
sleep 20
echo "Sleeping 20s... Filebeat starting"

gnome-terminal -t "Kafka" --tab -- sh kafka-start.sh
echo "Sleeping 15s... Kafka starting"
sleep 15

gnome-terminal -t "Logstash" --tab -- sh logstash-start.sh
echo "Sleeping 20s... Logstash starting"
sleep 20

gnome-terminal -t "Elasticsearch" --tab -- sh elasticsearch-start.sh
echo "Sleeping 20s... Elasticsearch starting"
sleep 20

gnome-terminal -t "Kibana" --tab -- sh kibana-start.sh
echo "Sleeping 20s... Kibana starting"
sleep 20

#echo "House starting"
#gnome-terminal -t "House" --tab -- sh house.sh
