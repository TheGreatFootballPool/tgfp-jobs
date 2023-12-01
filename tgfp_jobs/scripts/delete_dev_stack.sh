#!/usr/bin/env bash
# Creates and runs the docker DB in the development environment
#
docker rm --force tgfp-mongodb
docker rm --force tgfp-mqtt
docker rm --force tgfp-nag-bot