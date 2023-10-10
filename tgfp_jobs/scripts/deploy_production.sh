#!/usr/bin/env bash
set -o allexport
SCRIPTS_DIR="$(dirname "$0")"
cd $SCRIPTS_DIR
. ./create_prod_env.sh
source stack.env
cd $SCRIPTS_DIR
prefect --no-prompt deploy -n '*-prod'
set +o allexport
