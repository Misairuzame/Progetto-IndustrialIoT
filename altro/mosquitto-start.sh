#!/bin/bash

[ $(pgrep -cx mosquitto) -gt 0 ] && sudo kill $(pgrep -ox mosquitto) && echo -n "Waiting for old mosquitto instance to terminate..." && sleep 12
mosquitto -v
