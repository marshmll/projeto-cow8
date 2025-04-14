#!/usr/bin/bash

if [[ ! -z $1 ]]
then
    if [ $1 == "all" ]
    then
        echo "Starting Docker as a Daemon. Stop it using \"stop.sh\"."
        docker compose up --detach
        echo "Starting Flask"
        python -m flask --app app.py run --debug
    
    elif [ $1 == "docker" ]
    then
        echo "Building and Starting Docker"
        docker compose up --build --remove-orphans
    elif [ $1 == "flask" ]
    then
        echo "Starting Flask"
        python -m flask --app app.py run --debug
    fi
else
    echo "Usage: $0 <option>"
    echo "  <all>    - Start Docker as a Daemon and Flask"
    echo "  <docker> - Start only Docker" 
    echo "  <flask>  - Start only Flask" 
fi
