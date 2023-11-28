#!/bin/bash
echo "CDing to scripts"
cd /app/scripts
echo "Starting Worker Pool"
prefect worker start --pool 'tgfp-jobs'
