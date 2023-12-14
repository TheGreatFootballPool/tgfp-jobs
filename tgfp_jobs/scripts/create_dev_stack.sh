#!/usr/bin/env bash
# Creates and runs the docker DB in the development environment
#

# First we need to set up all the environment variables for development
echo "==== Setting up environment and moving to top level dir  ===="
set -o allexport
ENVIRONMENT=development
# Get scripts dir, and cd there
cd "$(dirname "$0")"
SCRIPTS_DIR="$(pwd)"
echo $SCRIPTS_DIR
# Building the stack environment file
echo "==== Creating the dev stack.env file ===="
op inject -f -i $SCRIPTS_DIR/op.env -o $SCRIPTS_DIR/stack.env
source $SCRIPTS_DIR/stack.env
set +o allexport


# get current machine's IP address
echo "=== Grabbing IP Address and updating prefect variable ==="
IP_ADDRESS=`ipconfig getifaddr en0`

# first update the mqtt host
update_variable() {
  VARIABLE_NAME=$1
  VARIABLE_ID=$2
  VARIABLE_VALUE=$3

  URL="$PREFECT_API_URL/variables/$VARIABLE_ID"
  # push new address to variable
  curl --location --request PATCH $URL \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $PREFECT_API_KEY" \
    --header "X-PREFECT-API-VERSION: 0.8.4" \
    --data-raw "{ \"name\": \"$VARIABLE_NAME\",\"value\": \"$VARIABLE_VALUE\"}"
}

update_variable "mqtt_host_development" "e624708d-22af-4d44-a4eb-43c27337c166" "$IP_ADDRESS"
update_variable "mongo_host_development" "813c632b-ba11-4a05-8765-5fb99db41350" "$IP_ADDRESS"

# Function definitions here
create_mongo_db() {
  echo "=== Creating the mongo DB ==="
  MONGODB_PROD_PASSWORD=`python prefect_fetch.py mongo-root-password-production`
  if [ "$( docker ps --filter 'name=tgfp-mongodb' --quiet)" ]; then
    echo "previous old db container exists, removing"
    docker rm --force tgfp-mongodb
  fi
  docker compose up -d tgfp-mongodb
}

restore_mongo_db_data() {
  echo "=== Resetting the DB from production data ==="
  MONGODB_PROD_PASSWORD=`python prefect_fetch.py mongo-root-password-production`
  docker exec tgfp-mongodb \
     /usr/bin/mongodump --username tgfp --password $MONGODB_PROD_PASSWORD --host='goshdarnedserver.lan:27017'
  docker exec tgfp-mongodb rm -rf dump/admin
  docker exec tgfp-mongodb \
     /usr/bin/mongorestore --username tgfp --password development dump/ --authenticationDatabase=admin --drop
}

create_mqtt() {
  echo "=== Creating the Mosquitto broker ==="
  if [ "$( docker ps --filter 'name=tgfp-mqtt' --quiet)" ]; then
    echo "previous old mqtt container exists, removing"
    docker rm --force tgfp-mqtt
  fi
  docker compose up -d tgfp-mqtt
}

create_tgfp_nag_bot() {
  echo "=== Creating the TGFP Bot ==="
  if [ "$( docker ps --filter 'name=tgfp-nag-bot' --quiet)" ]; then
    echo "previous old tgfp-nag-bot container exists, removing"
    docker rm --force tgfp-nag-bot
  fi
  docker compose up -d tgfp-nag-bot
}

read -n1 -p "Just create stack.env?" justenv
if [[ $justenv == "Y" || $justenv == "y" ]] ; then
  exit
fi
# Create and start the DB
# Reset the data in the DB
if [ "$( docker container inspect -f '{{.State.Running}}' tgfp-mongodb )" = "true" ]; then
  echo "* I found a running tgfp-mongo container."
  read -n1 -p "Recreate it [Y/N]: " recreate
  if [[ $recreate == "Y" || $recreate == "y" ]] ; then
    echo ""
    create_mongo_db && restore_mongo_db_data
  else
    printf "\nOK, Not recreating\n\n"
    printf "* Should we reset the data to match production?\n"
    read -n1 -p "Reset it [Y/N]: " reset
    if [[ $reset == "Y" || $reset == "y" ]] ; then
      echo ""
      restore_mongo_db_data
    else
      printf "\nGotcha, not resetting data\n"
    fi
  fi
else
  create_mongo_db && restore_mongo_db_data
fi

# Create and start the Mosquitto Broker
if [ "$( docker container inspect -f '{{.State.Running}}' tgfp-mqtt )" = "true" ]; then
  echo "* I found a running tgfp-mqtt container."
  read -n1 -p "Recreate it [Y/N]: " recreate
  if [[ $recreate == "Y" || $recreate == "y" ]] ; then
    echo ""
    create_mqtt
  else
    printf "\nOK, Not recreating\n\n"
  fi
else
  create_mqtt
fi

# Fire up the bot
if [ "$( docker container inspect -f '{{.State.Running}}' tgfp-nag-bot )" = "true" ]; then
  echo "* I found a running tgfp-nag-bot container."
  read -n1 -p "Recreate it [Y/N]: " recreate
  if [[ $recreate == "Y" || $recreate == "y" ]] ; then
    echo ""
    create_tgfp_nag_bot
  else
    printf "\nOK, Not recreating\n\n"
  fi
else
  create_tgfp_nag_bot
fi

