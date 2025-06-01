#!/bin/bash

set -euo pipefail

tmux new-session -d -s simulazione -n main
tmux setw pane-border-status top

# Mosquitto
tmux send-keys -t simulazione 'printf '\''\033]2;Mosquitto\033\\'\''; mosquitto -v' C-m

# Filebeat
tmux split-window -h -t simulazione
tmux send-keys -t simulazione 'printf '\''\033]2;Filebeat\033\\'\''; filebeat run -e' C-m

# Main
tmux split-window -h -t simulazione
tmux send-keys -t simulazione 'printf '\''\033]2;Main\033\\'\''; python main.py' C-m

# Riorganizza i pannelli in modo che siano leggibili
tmux select-layout -t simulazione tiled

while [ ! -f /app/log.ndjson ];
do
    sleep 1
done

tail -f /app/log.ndjson
