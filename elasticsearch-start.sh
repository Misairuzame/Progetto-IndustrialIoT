#!/bin/bash

sudo systemctl stop elasticsearch && sudo systemctl start elasticsearch && journalctl -f -u elasticsearch
