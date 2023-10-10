#!/usr/bin/env bash
set -o allexport
SCRIPTS_DIR="$(dirname "$0")"
cd $SCRIPTS_DIR
cd ../../
. ./create_dev_env.sh
source stack.env
cd $SCRIPTS_DIR
prefect --no-prompt deploy -n '*-dev'
set +o allexport
