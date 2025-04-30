#!/bin/bash

# Eseguire con "bash"
# Crea 10 case

if [ $# -ge 1 ]; then
    PORT=$1
else
    PORT=1884
fi

gnome-terminal -t "Casa "$PORT -- sh house.sh $PORT
((PORT++))
gnome-terminal -t "Casa "$PORT -- sh house.sh $PORT
((PORT++))
gnome-terminal -t "Casa "$PORT -- sh house.sh $PORT
((PORT++))
gnome-terminal -t "Casa "$PORT -- sh house.sh $PORT
((PORT++))
gnome-terminal -t "Casa "$PORT -- sh house.sh $PORT
((PORT++))
gnome-terminal -t "Casa "$PORT -- sh house.sh $PORT
((PORT++))
gnome-terminal -t "Casa "$PORT -- sh house.sh $PORT
((PORT++))
gnome-terminal -t "Casa "$PORT -- sh house.sh $PORT
((PORT++))
gnome-terminal -t "Casa "$PORT -- sh house.sh $PORT
((PORT++))
gnome-terminal -t "Casa "$PORT -- sh house.sh $PORT
