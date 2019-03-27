#!/bin/bash

PYTHONPATH="${PYTHONPATH}:/usr/src/RecordKeeperBot/discord_bot/"
export PYTHONPATH

/usr/bin/python3 /usr/src/RecordKeeperBot/discord_bot/scheduled/elo_calculator.py 

