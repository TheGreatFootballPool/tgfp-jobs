#!/bin/bash
echo "CDing to scripts"
cd /app/scripts
echo "Deploying Prefect"
prefect --no-prompt deploy --all
echo "Starting Worker Pool"
prefect worker start --pool 'tgfp-jobs'