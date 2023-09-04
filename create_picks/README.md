# Create the picks page

Job scheduled for creating the picks page

## Configuration for Portainer

### Make sure the scripts are updated to the latest in the `tgfp` repo on `goshdarnedserver`
1. ssh goshdarnedserver
2. cd ~/tgfp
3. git fetch
4. git pull --rebase

Add the service in the [docker-compose.yaml](docker-compose.yaml) to the Portainer Stack
Add the variables listed in the docker compose file to the Portainer Stack
