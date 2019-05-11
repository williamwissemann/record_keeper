from Storage import UserStats
from RecordKeeperFunc import RecordKeeper
from RecordKeeperUtils import message_parser

import RecordKeeperViews as bot_message


import discord
import asyncio
import random
import datetime
import math
import time
import sys
import json
import os

os.chdir(os.path.abspath(__file__).replace("RecordKeeperBot.py", ""))
# Load in json file to initialize the bot
path = os.path.realpath(__file__).rstrip(".py")
with open(path + ".json") as f:
    settings = json.load(f)
    environment = settings[settings["settings"]["environment"]]
    dev_environment = settings["development"]
# create discord client
client = discord.Client()
# create database handler
keeper = RecordKeeper("/usr/src/RecordKeeperBot/database/" + environment["database"])


@client.event
async def on_ready():
    """ bot is ready """
    try:
        """ print bot information """
        print("> signed in as: " + client.user.name)
        print("> with client id: " + client.user.id)
        print('> Discord.py Version: {}'.format(discord.__version__))
    except Exception as e:
        print(e)


@client.event
async def on_message(message):
    """ on new message """
    # restrict DMs to bot members
    member_found = False
    for server in client.servers:
        member_found = message.author in server.members

    # lock to specified channels
    on_bot_channel = True
    if message.server:
        if (not str(message.channel) == settings["production"]["discord_channel"] and
                not str(message.channel) == settings["development"]["discord_channel"]):
            on_bot_channel = False

    # setup testing-bot to ignore prod channels
    expected_channel = environment['discord_channel']
    if expected_channel == dev_environment['discord_channel']:
        if str(message.channel) != expected_channel:
            print("testing-bot ignore " + str(message.channel))
            return False

    # setup prod-bot to ignore testing channels
    if (str(message.channel) == dev_environment['discord_channel'] and
            expected_channel != dev_environment['discord_channel']):
        print(prod_channel + " stay away")
        return False

    user_msg = message_parser(message.content)
    if not user_msg:
        return True
    user_msg["raw_msg"] = message
    user_msg["client"] = client
    if user_msg and member_found and on_bot_channel:
        update_message = await client.send_message(message.channel, 'updating....')
        bot_msg = None

        print(user_msg)
        if user_msg["cmd"].lower() == 'help':
            # creates the help page
            bot_msg = keeper.help()
        elif user_msg["cmd"].lower() == 'medals':
            # creates the medal list help page
            bot_msg = keeper.medals()
        elif user_msg["cmd"].lower() == 'raid':
            # generate the raid list help page
            bot_msg = keeper.raid(user_msg)
        elif user_msg["cmd"].lower() == 'up':
            # updates a given stat
            bot_msg = keeper.up(user_msg)
        elif user_msg["cmd"].lower() == 'ls':
            # lists stats for a given user
            bot_msg = keeper.ls(user_msg)
        elif user_msg["cmd"].lower() == 'lb':
            # creates a leaderboard for a given stat
            bot_msg = keeper.lb(user_msg)
        elif user_msg["cmd"].lower() == 'add-player':
            # manually add player to track player outside discord
            bot_msg = keeper.add_player(user_msg)
        elif user_msg["cmd"].lower() == 'uuid':
            # generate uuid(s) table
            bot_msg = keeper.uuid(user_msg)
        elif user_msg["cmd"].lower() == 'del':
            # delete a data point based a (medal, uuid) pair
            bot_msg = keeper.delete(user_msg)
        elif user_msg["cmd"].lower() == 'pvp':
            # handles pvp win / lose
            bot_msg = keeper.pvp(user_msg)
        elif user_msg["cmd"].lower() == 'want':
            # adds wanted pokemon to tradeboard
            bot_msg = keeper.want(user_msg)
        elif user_msg["cmd"].lower() == 'unwant':
            # delete unwanted pokemon from tradeboard
            bot_msg = keeper.unwant(user_msg)
        elif user_msg["cmd"].lower() == 'tbu':
            # list tradeboard by user
            bot_msg = keeper.tbu(user_msg)
        elif user_msg["cmd"].lower() == 'tbs':
            # generates a search string for a user
            bot_msg = keeper.tbs(user_msg)
        elif user_msg["cmd"].lower() == 'tbp':
            # generates a tradeboard for a given pokemon
            bot_msg = keeper.tbp(user_msg)
        elif user_msg["cmd"].lower() == 'roll' or user_msg["cmd"].lower() == 'd20':
            # allow for global server commands
            pass
        else:
            await client.edit_message(
                update_message,
                "Bidoof, sorry, something went wrong, try !help for more info")

        if bot_msg:
            await client.edit_message(update_message, bot_msg)

    # global_command
    if user_msg["cmd"].lower() == 'roll' or user_msg["cmd"].lower() == 'd20':
        # dice rolls d6
        await client.edit_message(update_message, "rolling...")
        await asyncio.sleep(2)
        if len(user_msg["args"]) > 0:
            counter = random.randint(1, int(user_msg["args"][0]))
        elif user_msg["cmd"].lower() == 'd20':
            counter = random.randint(1, 20)
        else:
            counter = random.randint(1, 6)
        bot_msg = '{} rolled a {}'.format(message.author.name, counter)
        await client.edit_message(update_message, bot_msg)

# starts bot
if __name__ == "__main__":
    # token from https://discordapp.com/developers
    client.run(settings["settings"]["discord_token"])
