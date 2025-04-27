#!/bin/bash

sudo /usr/share/logstash/bin/logstash --path.settings /etc/logstash -f ./logstash-config.cfg
