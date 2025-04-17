#!/usr/bin/bash

if [[ ! -z $1 ]]
then
    if [ $1 == "all" ]
    then
        echo "Starting Docker as a Daemon. Stop it using \"stop.sh\"." &&
        docker compose up --detach &&
        echo "Starting Flask"
        sleep 5
        source .venv/bin/activate &&
        python -m flask --app . run --debug
        exit 0
    elif [ $1 == "docker" ]
    then
        echo "Building and Starting Docker" &&
        docker compose up --build --remove-orphans
        exit 0
    elif [ $1 == "flask" ]
    then
        echo "Starting Flask" &&
        source .venv/bin/activate &&
        python -m flask --app . run --debug
        exit 0
    else
        echo "Unknown option: \"$1\""
        exit 1
    fi
else
    echo "Usage: $0 <option>"
    echo "  <all>    - Start Docker as a Daemon and Flask"
    echo "  <docker> - Start only Docker" 
    echo "  <flask>  - Start only Flask"
    exit 0
fi
