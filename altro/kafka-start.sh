#!/bin/bash

sudo systemctl stop kafka && sudo systemctl start kafka && journalctl -f -u kafka
