#!/usr/bin/env bash
# usage: [major, minor, patch] "commit message"
# Get poetry version
set -o allexport
ENVIRONMENT=development
echo "==== Setting up environment and moving to top level dir  ===="

# Get scripts dir, and cd there
cd "$(dirname "$0")"
SCRIPTS_DIR="$(pwd)"
echo $SCRIPTS_DIR

echo "==== Getting poetry version ===="
NEW_VERSION=`poetry version -s`
echo "==== Poetry version: $NEW_VERSION ===="

# Building the stack environment file
op inject -f -i $SCRIPTS_DIR/op.env -o $SCRIPTS_DIR/stack.env
source $SCRIPTS_DIR/stack.env

echo "==== Deploying production flows to prefect ===="
prefect --no-prompt deploy -n '*-dev'
set +o allexport

echo "==== Starting dev worker pool ===="
prefect worker start --pool 'tgfp-development'