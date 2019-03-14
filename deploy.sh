#!/bin/bash

NAME=${1:-airbus}
PORT=${2:-8001}

git pull

echo Building Docker image ...
docker build -t $NAME .

echo Running container ...
docker run --name $NAME -d -p $PORT:5000 --rm --env-file=.env $NAME

echo Deleting unused images
docker image prune -f

echo Beginning the logging -- CTRL+c to esacpe logs.
docker logs --tail 350 -f $NAME
