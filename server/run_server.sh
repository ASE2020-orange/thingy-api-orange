#!/bin/bash

#set -e

exec python3.7 ./server.py & 
# add delay so the server can create the websockets etc.
sleep 5
exec python3.7 ./thingy.py 