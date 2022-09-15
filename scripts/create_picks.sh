#!/usr/bin/env bash
source /.env
cd /scripts
doppler run --token $DOPPLER_TOKEN --command="python create_picks.py"
curl -m 10 --retry 5 https://hc-ping.com/ae09aed7-ec22-47f6-9e1a-67ab5421aec3