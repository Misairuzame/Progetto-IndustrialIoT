#!/bin/bash

sudo service kibana stop && sudo service kibana start && journalctl -f -u kibana
