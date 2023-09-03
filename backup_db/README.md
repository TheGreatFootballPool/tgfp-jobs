# Backup DB

Backs up the production database and creates a rotated backup file.

## Configuration for Portainer

### Make sure the scripts are updated to the latest in the `tgfp` repo on `goshdarnedserver`
1. ssh goshdarnedserver
2. cd ~/tgfp
3. git fetch
4. git pull --rebase

Add the service in the [docker-compose.yaml](docker-compose.yaml)
Add the following env variables to the stack
```dotenv
TGFP_HOME
TZ=US/Pacific
MONGO_BACKUP_DIR
MONGO_URI
HEALTHCHECK_URL_DB_BACKUP
```