#!/bin/bash

NAME=${1:-airbus}
PORT=${2:-8001}
REDEPLOY=${3:-0}
LOGS=${4:-0}

echo Pulling latest git
git pull

if [$REDEPLOY != 0] 
then
    echo stopping container airbus 
    docker container stop $NAME
    echo removing container airbus
    docker container rm airbus
fi 

echo Building Docker image ...
docker build -t $NAME .

echo Running container ...
docker run --name $NAME -d -p $PORT:5000 --rm --env-file=.env $NAME

echo Deleting unused images
docker image prune -f

if [$LOGS != 0]
then
    echo Beginning the logging -- CTRL+c to esacpe logs.
    docker logs --tail 350 -f $NAME
fi 