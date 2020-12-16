# README

## .env file
do not forget to set the `.env` file based on `.env.sample`

## DB diagram
https://dbdiagram.io/d/5fa2c0713a78976d7b7a8403

## Run

First setup your MQTT Thingy config in the `server/.env`file.

You need to have docker installed on your machine.

You need to clone the client repo: https://github.com/ASE2020-orange/thingy-client-orange

Then build the client container in the thingy-client-orange root folder: `docker build -t thingy-client-orange .`

Then using the a bash interpreter go to the root folder of the thingy-api-orange project.

Run the script `run_services.sh` and wait for it to end.

## Stop

Run the command `docker-compose down`.
