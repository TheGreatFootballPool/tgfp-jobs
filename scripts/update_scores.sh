#!/bin/bash

SCRIPT_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
SCRIPT_NAME="update_scores"
cd $SCRIPT_PATH
curl -m 10 --retry 5 https://hc-ping.com/26764645-4b82-4002-af99-48cb34b07b2f
nohup poetry run python ${SCRIPT_PATH}/${SCRIPT_NAME}.py > logs/${SCRIPT_NAME}.out 2> logs/${SCRIPT_NAME}.err < /dev/null &