#!/bin/bash

#set -e

python3.7 ./tests.py && exec python3.7 ./server.py & 
# add delay so the server can create the websockets etc.
sleep 2
exec python3.7 ./thingy.py 