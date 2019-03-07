#!/bin/bash

# exits on ctrl+c
trap "echo Exited!; exit 0;" SIGINT

PYTHONPATH="${PYTHONPATH}:/usr/src/RecordKeeperBot/discord_bot/"
export PYTHONPATH

# create crontab jobs
echo "google sheets export scheduled"
echo "0 */4 * * * /usr/src/RecordKeeperBot/discord_bot/scheduled/toSheets.sh" >> dynamic_cron
echo "elo calculator scheduled"
echo "0 */1 * * * /usr/src/RecordKeeperBot/discord_bot/scheduled/elo_calculator.sh" >> dynamic_cron

# install new cron file
crontab dynamic_cron
rm dynamic_cron

# keeps the discord bot runing forever  
while true ; do
    echo "bot starting..."
    pgrep -f RecordKeeperBot.py || /usr/bin/python3 /usr/src/RecordKeeperBot/discord_bot/RecordKeeperBot.py "${@}" 
    echo "Failed Restarting!"
    sleep 60
done 

# force a clean exit so docker-compose will restart the container
exit 0;