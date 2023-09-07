#!/bin/bash
# usage: [major, minor, patch] "commit message"
STOP=`find . -name '*.env' -exec grep -c "DO NOT COMMIT" {} \; | grep -c 1`
if [ $STOP == 1 ] ; then
  echo "SECRETS IN COMMIT -- Exiting"
  exit 1
fi
poetry version $1
git add .
git commit -m "$2"
git push
NEW_VERSION=`poetry version -s`
git tag v${NEW_VERSION}
git push origin v${NEW_VERSION}
# TODO: Add code to push to the production server via ssh
