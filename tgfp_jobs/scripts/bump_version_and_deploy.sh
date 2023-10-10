#!/usr/bin/env bash
# usage: [major, minor, patch] "commit message"
# Get poetry version
export ENVIRONMENT=production
echo "==== Setting up environment and moving to top level dir  ===="

# Get scripts dir, and cd there
SCRIPTS_DIR="$(dirname "$0")"
cd $SCRIPTS_DIR

echo "==== Getting poetry version ===="
poetry version $1
export NEW_VERSION=`poetry version -s`
echo "==== Poetry version: $NEW_VERSION ===="

echo "==== Adding / committing / tagging ===="
cd ../../
git add .
git commit -m "$2"
git push
git tag v${NEW_VERSION}
git push origin ${NEW_VERSION}
cd $SCRIPTS_DIR

echo "==== Pushing code to server production server ===="
ssh goshdarnedserver.lan 'cd ~/tgfp ; git pull --rebase'

# Building the stack environment file
op inject -f -i op.env -o stack.env
set -o allexport
source stack.env

echo "==== Deploying production flows to prefect ===="
prefect --no-prompt deploy -n '*-prod'
set +o allexport
