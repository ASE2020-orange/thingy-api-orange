# README

## .env file
Copy the `.env.sample` file at the root of the server folder and name it `.env`, fill up your parameters.
## DB diagram
https://dbdiagram.io/d/5fda90949a6c525a03bb5ee2

## Run

You need to have your MQTT Thingy setup with the config in the `server/.env`file.

You need to have docker installed on your machine.

You need to clone the client repo: https://github.com/ASE2020-orange/thingy-client-orange

Then build the client container in the thingy-client-orange root folder: `docker build -t thingy-client-orange .`

Then using the a bash interpreter go to the root folder of the thingy-api-orange project.

Run the command `docker-compose up` or `docker-compose up --build` if you never built the containers and wait for it to end.

## Stop

Run the command `docker-compose down`.
