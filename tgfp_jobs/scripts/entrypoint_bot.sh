#!/bin/bash
echo "CDing to scripts"
cd /app/scripts
python -V
echo "Starting Bot"
python3.11 bot.py
