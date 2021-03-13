#!/bin/bash

# exits on ctrl+c
trap "echo Exited!; exit 0;" SIGINT

# keeps the discord bot runing forever  
while true ; do
    echo "bot starting..."
    pgrep -f app.py || ./venv/bin/python3 /app/venv/lib/python3.8/site-packages/record_keeper/app.py
    echo "failed restarting!"
    sleep 60
done 

# force a clean exit so docker-compose will restart the container
exit 0;