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
        print("> with client id: " + str(client.user.id))
        print('> Discord.py Version: {}'.format(discord.__version__))
    except Exception as e:
        print(e)


@client.event
async def on_message(message):
    """ on new message """
    # restrict DMs to bot members
    member_found = False
    for guild in client.guilds:
        member_found = message.author in guild.members
        if member_found:
            break

    # lock to specified channels
    on_bot_channel = True
    if message.guild:
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
        print("prod-bot stay away")
        return False

    user_msg = message_parser(message.content)
    if user_msg == "spacing issue":
        await message.channel.send("You're missing a space somewhere in the command")
        return True
    if not user_msg:
        return True
    user_msg["raw_msg"] = message
    user_msg["client"] = client
    if user_msg and member_found and on_bot_channel:
        delete_msg = False
        bot_msg = None

        print(str(user_msg).encode('utf-8'))
        if user_msg["cmd"].lower() == 'help' and settings["settings"]["help"]:
            # creates the help page
            await message.channel.send(keeper.help())
        elif user_msg["cmd"].lower() == 'medals' and settings["settings"]["help"]:
            # creates the medal list help page
            await message.channel.send(keeper.medals())
        elif user_msg["cmd"].lower() == 'raid' and settings["settings"]["help"]:
            # generate the raid list help page
            await message.channel.send(keeper.raid(user_msg))
        elif user_msg["cmd"].lower() == 'up' and settings["settings"]["record-keeping"]:
            # updates a given stat
            await message.channel.send(keeper.up(user_msg))
        elif (user_msg["cmd"].lower() == 'ls' and
              (settings["settings"]["record-keeping"] or settings["settings"]["elo"])):
            # lists stats for a given user
            await message.channel.send(keeper.ls(user_msg))
        elif (user_msg["cmd"].lower() == 'lb' and
              (settings["settings"]["record-keeping"] or settings["settings"]["elo"])):
            # creates a leaderboard for a given stat
            await message.channel.send(keeper.lb(user_msg))
        elif user_msg["cmd"].lower() == 'add-player' and settings["settings"]["elo"]:
            # manually add player to track player outside discord
            await message.channel.send(keeper.add_player(user_msg))
        elif user_msg["cmd"].lower() == 'uuid' and settings["settings"]["record-keeping"]:
            # generate uuid(s) table
            await message.channel.send(keeper.uuid(user_msg))
        elif user_msg["cmd"].lower() == 'del' and settings["settings"]["record-keeping"]:
            # delete a data point based a (medal, uuid) pair
            await message.channel.send(keeper.delete(user_msg))
        elif user_msg["cmd"].lower() == 'pvp' and settings["settings"]["elo"]:
            # handles pvp win / lose
            await message.channel.send(keeper.pvp(user_msg))
        elif user_msg["cmd"].lower() == 'want' and settings["settings"]["trading"]:
            # adds wanted pokemon to tradeboard
            await message.channel.send(keeper.want(user_msg))
        elif user_msg["cmd"].lower() == 'unwant' and settings["settings"]["trading"]:
            # delete unwanted pokemon from tradeboard
            await message.channel.send(keeper.unwant(user_msg))
        elif user_msg["cmd"].lower() == 'tbu' and settings["settings"]["trading"]:
            # list tradeboard by user
            await message.channel.send(keeper.tbu(user_msg))
        elif user_msg["cmd"].lower() == 'tbs' and settings["settings"]["trading"]:
            # generates a search string for a user
            await message.channel.send(keeper.tbs(user_msg))
        elif user_msg["cmd"].lower() == 'tbp' and settings["settings"]["trading"]:
            # generates a tradeboard for a given pokemon
            await message.channel.send(keeper.tbp(user_msg))
        elif ((user_msg["cmd"].lower() == 'add-friend' or user_msg["cmd"].lower() == 'auf') and
              settings["settings"]["matchmaking"]):
            # add friend to friends list
            update_message = await message.channel.send("updating...")
            await update_message.edit(content=keeper.addfriend(user_msg))
        elif ((user_msg["cmd"].lower() == 'remove-friend' or user_msg["cmd"].lower() == 'ruf') and
              settings["settings"]["matchmaking"]):
            # remove friend from friends list
            update_message = await message.channel.send("updating...")
            await update_message.edit(content=keeper.removefriend(user_msg))
        elif user_msg["cmd"].lower() == "friends" and settings["settings"]["matchmaking"]:
            # list friends friends list
            await message.channel.send(keeper.list_friends(user_msg))
        elif user_msg["cmd"].lower() == 'online' and settings["settings"]["matchmaking"]:
            # set status to online
            await message.channel.send(keeper.online(user_msg))
        elif user_msg["cmd"].lower() == 'offline' and settings["settings"]["matchmaking"]:
            # set status to offline
            await message.channel.send(keeper.offline(user_msg))
        elif ((user_msg["cmd"].lower() == 'ping-friends' or user_msg["cmd"].lower() == 'ltb') and
                settings["settings"]["matchmaking"]):
            # ping friends user is looking for match
            await message.channel.send(keeper.ping_friends(user_msg))
        elif user_msg["cmd"].lower() == 'roll' or user_msg["cmd"].lower() == 'd20':
            # allow for global commands
            pass
        else:
            if settings["settings"]["try_help_message"]:
                try:
                    await update_message.edit(
                        content="Bidoof, sorry, something went wrong, try !help for more info")
                except:
                    await message.channel.send("Bidoof, sorry, something went wrong, try !help for more info")

    # global_command
    if ((user_msg["cmd"].lower() == 'roll' or user_msg["cmd"].lower() == 'd20') and
            settings["settings"]["global_commands"]):
        try:
            await update_message.edit(content="rolling...")
        except:
            update_message = await message.channel.send("rolling...")
        # dice rolls d6
        await asyncio.sleep(2)
        if len(user_msg["args"]) > 0:
            counter = random.randint(1, int(user_msg["args"][0]))
        elif user_msg["cmd"].lower() == 'd20':
            counter = random.randint(1, 20)
        else:
            counter = random.randint(1, 6)
        bot_msg = '{} rolled a {}'.format(message.author.name, counter)
        await update_message.edit(content=bot_msg)

# starts bot
if __name__ == "__main__":
    # token from https://discordapp.com/developers
    client.run(settings["settings"]["discord_token"])
