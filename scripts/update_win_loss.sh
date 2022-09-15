#!/usr/bin/env bash
source /.env
cd /scripts
doppler run --token $DOPPLER_TOKEN --command="python update_win_loss.py"