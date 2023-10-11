#!/usr/bin/env bash
# usage: [major, minor, patch] "commit message"
# Get poetry version
set -o allexport
ENVIRONMENT=production
echo "==== Setting up environment and moving to top level dir  ===="

# Get scripts dir, and cd there
cd "$(dirname "$0")"
SCRIPTS_DIR="$(pwd)"
echo $SCRIPTS_DIR

echo "==== Getting poetry version ===="
poetry version $1
NEW_VERSION=`poetry version -s`
echo "==== Poetry version: $NEW_VERSION ===="

echo "==== Adding / committing / tagging ===="
cd ../../
git add .
git commit -m "$2"
git push
git tag v${NEW_VERSION}
git push origin v${NEW_VERSION}
cd $SCRIPTS_DIR

echo "==== Pushing code to server production server ===="
ssh goshdarnedserver.lan 'cd ~/tgfp ; git pull --rebase'

set -xv
# Building the stack environment file
op inject -f -i $SCRIPTS_DIR/op.env -o $SCRIPTS_DIR/stack.env
source $SCRIPTS_DIR/stack.env

echo "==== Deploying production flows to prefect ===="
prefect --no-prompt deploy -n '*-prod'
set +o allexport
