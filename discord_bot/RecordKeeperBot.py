from Storage import UserStats
from RecordKeeperFunc import RecordKeeper

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

    expected_channel = environment['discord_channel']
    if expected_channel == dev_environment['discord_channel']:
        if str(message.channel) != expected_channel:
            print("testing-bot ignore " + str(message.channel))
            return False

    if (str(message.channel) == dev_environment['discord_channel'] and
            expected_channel != dev_environment['discord_channel']):
        print(prod_channel + " stay away")
        return False

    if message.content.startswith('!'):
        update_message = await client.send_message(message.channel, 'updating....')
        bot_msg = "oops, that shouln't have happened"
        if message.content.startswith('!help'):
            # creates the help page"
            bot_msg = keeper.help()
        elif message.content.startswith('!medals'):
            # creates the medal list help page"
            bot_msg = keeper.medals(message)
        elif message.content.startswith('!raid'):
            # generate the raid list help page"
            bot_msg = keeper.raid(message)
        elif message.content.startswith('!up'):
            # updates a given stat
            bot_msg = keeper.up(message)
        elif message.content.startswith('!ls'):
            # lists stats for a given user
            bot_msg = keeper.ls(message)
        elif message.content.startswith('!lb'):
            # creates a leaderboard for a given stat
            bot_msg = keeper.lb(message)
        elif message.content.startswith('!add-player'):
            # manually add player to track player outside discord
            bot_msg = keeper.add_player(message)
        elif message.content.startswith('!uuid'):
            # generate uuid(s) table
            bot_msg = keeper.uuid(message)
        elif message.content.startswith('!del'):
            # delete a data point based a (medal, uuid) pair
            bot_msg = keeper.delete(message)
        elif message.content.startswith('!pvp'):
            # handles pvp win / lose
            bot_msg = keeper.pvp(message)
        elif message.content.startswith('!want'):
            # adds wanted pokemon to tradeboard
            bot_msg = keeper.want(message)
        elif message.content.startswith('!unwant'):
            # delete unwanted pokemon from tradeboard
            bot_msg = keeper.unwant(message)
        elif message.content.startswith('!tbu'):
            # list tradeboard by user
            bot_msg = keeper.tbu(message)
        elif message.content.startswith('!tbs'):
            # generates a search string for a user
            bot_msg = keeper.tbs(message)
        elif message.content.startswith('!tbp'):
            # generates a tradeboard for a given user
            bot_msg = keeper.tbp(message)
        elif message.content.startswith('!roll'):
            # dice rolls d6
            await client.edit_message(update_message, "rolling...")
            await asyncio.sleep(2)
            counter = random.randint(1, 6)
            bot_msg = '{} rolled a {}'.format(message.author.name, counter)
        elif message.content.startswith('!d20'):
            # dice rolls d20
            await client.edit_message(update_message, "rolling...")
            await asyncio.sleep(2)
            counter = random.randint(1, 20)
            bot_msg = '{} rolled a {}'.format(message.author.name, counter)
        else:
            await client.edit_message(
                update_message,
                "Bidoof, sorry, something went wrong, try !help for more info"
            )
        await client.edit_message(update_message, bot_msg)

# starts bot
if __name__ == "__main__":
    # token from https://discordapp.com/developers
    client.run(settings["settings"]["discord_token"])
