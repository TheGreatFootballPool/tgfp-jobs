#!/usr/bin/env bash
sudo docker compose down --rmi local
git stash save
git pull --rebase
git stash pop
sudo docker compose up -d