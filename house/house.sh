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

# Primo pannello: Mosquitto
tmux send-keys -t simulazione 'printf '\''\033]2;Mosquitto\033\\'\''; mosquitto -p '"$PORT"' -v' C-m

# Secondo pannello: Controller di Carica
tmux split-window -h -t simulazione
tmux send-keys -t simulazione 'printf '\''\033]2;Controller di Carica\033\\'\''; python charge_controller.py '"$PORT" C-m

# Terzo pannello: Quadro Elettrico
tmux split-window -v -t simulazione:0.0
tmux send-keys -t simulazione 'printf '\''\033]2;Quadro Elettrico\033\\'\''; python electric_panel.py '"$PORT" C-m

# Quarto pannello: Pannelli Solari
tmux split-window -v -t simulazione:0.1
tmux send-keys -t simulazione 'printf '\''\033]2;Pannelli Solari\033\\'\''; python panel_spawner.py '"$PORT" C-m

# Quinto pannello: Contatore SMART
tmux split-window -v -t simulazione:0.2
tmux send-keys -t simulazione 'printf '\''\033]2;Contatore SMART\033\\'\''; python subscriber.py '"$PORT" C-m

# Sesto pannello: Filebeat
tmux split-window -h -t simulazione:0.3
tmux send-keys -t simulazione 'printf '\''\033]2;Filebeat\033\\'\''; filebeat run -e' C-m

# Riorganizza i pannelli in modo che siano leggibili
tmux select-layout -t simulazione tiled

# Attach alla sessione
#tmux attach-session -t simulazione

while [ ! -f /app/log.ndjson ];
do
    sleep 1
done

tail -f /app/log.ndjson
