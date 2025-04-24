#!/bin/bash

docker compose down
docker image rm $(docker image ls -q) -f
docker compose up -d
docker exec -itu root spiderfoot sh
