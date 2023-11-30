# All TGFP Jobs / background processes

Master scheduler for all tgfp jobs

## Configuration for Portainer

### Make sure the scripts are updated to the latest in the `tgfp` repo on `goshdarnedserver`
1. ssh goshdarnedserver
2. cd ~/tgfp
3. git fetch
4. git pull --rebase

Add the service in the [docker-compose.yaml](docker-compose.yaml) to the Portainer Stack
Add the variables listed in the docker compose file to the Portainer Stack


## Configure the development environment

### Create or Re-Create the local dev DB
* Run `dev_create_db.sh`
### Fire up a local mosquitto broker
* Run `dev_create_mosquitto.sh`
1. Open the `tgfp-web` pycharm project and fire up a development stack on localhost
2. Run 