#!/usr/bin/env bash
source /.env
cd /scripts
doppler run --token $DOPPLER_TOKEN -- python update_win_loss.py
curl -m 10 --retry 5 https://hc-ping.com/26764645-4b82-4002-af99-48cb34b07b2f