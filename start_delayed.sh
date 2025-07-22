#!/bin/bash

# Warte 10 Sekunden
sleep 10

# Wechsle zum Spielverzeichnis
cd /home/twgbyrinth-Game

# Starte das Spiel
python3 main.py

# Falls das Spiel beendet wird, warte kurz und starte neu
sleep 5
python3 main.py 