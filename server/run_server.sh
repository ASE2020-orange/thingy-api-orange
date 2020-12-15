#!/bin/bash

#set -e

exec python3.7 ./server.py &
sleep 1
exec python3.7 ./thingy.py