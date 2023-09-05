# Backup DB

Backs up the production database and creates a rotated backup file.

## Configuration for Portainer

### Make sure the scripts are updated to the latest in the `tgfp` repo on `goshdarnedserver`
1. ssh goshdarnedserver
2. cd ~/tgfp
3. git fetch
4. git pull --rebase

Add the service in the [docker-compose.yaml](docker-compose.yaml) to the Portainer Stack
Add the variables listed in the docker compose file to the Portainer Stack


## Configure the development environment

1. Open the `tgfp-web` pycharm project and fire up a development stack on localhost