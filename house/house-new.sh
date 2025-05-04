#!/bin/bash

set -euo pipefail

if [ $# -ge 1 ];
then
    PORT=$1
else
    PORT=1883
fi

tmux new-session -d -s simulazione -n main
tmux setw pane-border-status top

# Mosquitto
tmux send-keys -t simulazione 'printf '\''\033]2;Mosquitto\033\\'\''; mosquitto -p '"$PORT"' -v' C-m

# Filebeat
tmux split-window -h -t simulazione
tmux send-keys -t simulazione 'printf '\''\033]2;Filebeat\033\\'\''; filebeat run -e' C-m

# Main
tmux split-window -h -t simulazione
tmux send-keys -t simulazione 'printf '\''\033]2;Main\033\\'\''; python main.py '"$PORT" C-m

# Riorganizza i pannelli in modo che siano leggibili
tmux select-layout -t simulazione tiled

# Attach alla sessione
#tmux attach-session -t simulazione

while [ ! -f /app/log.ndjson ];
do
    sleep 1
done

tail -f /app/log.ndjson
