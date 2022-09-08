#!/bin/sh
cd /app
while true
do
  python update_scores.py
  curl -m 10 --retry 5 https://hc-ping.com/26764645-4b82-4002-af99-48cb34b07b2f
  sleep 300
done
