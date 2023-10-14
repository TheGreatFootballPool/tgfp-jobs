#!/usr/bin/env bash
export ENVIRONMENT=development
cd "$(dirname "$0")"
SCRIPTS_DIR="$(pwd)"
op inject -f -i $SCRIPTS_DIR/op.env -o $SCRIPTS_DIR/stack.env
