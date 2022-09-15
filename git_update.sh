#!/usr/bin/env bash
git stash save
git pull --rebase
git stash pop