#!/bin/bash

if [ $# -ge 1 ];
then
    PORT=$1
else
    PORT=1883
fi

gnome-terminal -t "Mosquitto" --tab -- mosquitto -p $PORT -v
gnome-terminal -t "Controller di Carica" --tab -- python3 charge_controller.py $PORT
gnome-terminal -t "Quadro Elettrico" --tab -- python3 electric_panel.py $PORT
gnome-terminal -t "Pannelli Solari" --tab -- python3 panel_spawner.py $PORT
gnome-terminal -t "Contatore SMART" --tab -- python3 subscriber.py $PORT
