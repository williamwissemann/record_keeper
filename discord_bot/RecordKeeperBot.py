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

database_version = '1.0.1'

os.chdir(os.path.abspath(__file__).replace("RecordKeeperBot.py", ""))
RecordKeeperBotJson = os.path.realpath(__file__).rstrip(".py")

# Load in json file to initialize the bot
client = discord.Client(max_messages=100000)
with open(RecordKeeperBotJson + ".json") as f:
    settings = json.load(f)
    bot_environment = settings["bot_settings"]["environment"]
    # this logic needs fixing (via admin activate/deactiviate)
    environment = settings["bot_settings"][settings["bot_settings"]["environment"]]
    dev_environment = settings["bot_settings"]["development"]

db_path = "{}{}".format(
    "/usr/src/RecordKeeperBot/database/",
    settings["bot_settings"][bot_environment]["database"])

keeper = RecordKeeper(db_path, database_version)


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

async def send_message(view, dm_message, user_msg, delete_time, edit=False):
    if view:
        if not isinstance(view, list):
            view = [view]

        cleanup = keeper.has_listener(user_msg, "message-cleanup")

        for msg in view:
            if edit:
                update_message = await user_msg["raw_msg"].channel.send("updating...")
                if cleanup:
                    await update_message.edit(content=msg, delete_after=delete_time)
                else:
                    await update_message.edit(content=msg)
            else:
                if cleanup:
                    await user_msg["raw_msg"].channel.send(msg, delete_after=delete_time)
                else:
                    await user_msg["raw_msg"].channel.send(msg)

        if keeper.has_listener(user_msg, "message-cleanup") and not dm_message:
            await user_msg["raw_msg"].delete()


@client.event
async def on_message(message):
    checkpoint_one = False
    dm_message = False
    if "Direct Message" in str(message.channel):
        checkpoint_one = True
        dm_message = True
    if bot_environment == "development" and "-testing" not in str(message.channel):
        print("(dev) ignore message because of '-testing' flag")
    elif bot_environment == "production" and "-testing" in str(message.channel):
        print("(prod) ignore  message because of '-testing' flag")
    else:
        checkpoint_one = True
    if checkpoint_one and not message.author.bot:
        user_msg = message_parser(message.content)
        if user_msg:
            checkpoint_two = True
            if user_msg == "spacing issue":
                await message.channel.send("You're missing a space somewhere in the command")
            if not dm_message and message.author.guild_permissions.administrator:
                user_msg["raw_msg"] = message
                user_msg["client"] = client
                if user_msg["cmd"].lower() == 'setup':
                    checkpoint_two = False
                    await message.channel.send(keeper.setup(user_msg), delete_after=600)
                    if not dm_message:
                        await message.delete()
                elif user_msg["cmd"].lower() == 'activate':
                    checkpoint_two = False
                    if len(user_msg["args"]) > 0:
                        await message.channel.send(keeper.activate(user_msg), delete_after=60)
                        if not dm_message:
                            await message.delete()
                elif user_msg["cmd"].lower() == 'deactivate':
                    checkpoint_two = False
                    await message.channel.send(keeper.deactivate(user_msg), delete_after=60)
                    if not dm_message:
                        await message.delete()
                elif user_msg["cmd"].lower() == 'active':
                    checkpoint_two = False
                    await message.channel.send(keeper.list_listener(user_msg), delete_after=90)
                    if not dm_message:
                        await message.delete()
            if user_msg and not user_msg == "spacing issue":
                user_msg["raw_msg"] = message
                user_msg["client"] = client
                bot_msg = None
                if user_msg["cmd"].lower() == 'donate':
                    view = keeper.helpDonateLink()
                    await send_message(view, dm_message, user_msg, 120, edit=True)
                elif user_msg["cmd"].lower() == 'help' and keeper.has_listener(user_msg, "help"):
                    # creates the help page
                    view = keeper.help(user_msg)
                    await send_message(view, dm_message, user_msg, 120, edit=True)
                elif user_msg["cmd"].lower() == 'medals' and keeper.has_listener(user_msg, "help"):
                    # creates the medal list help page
                    view = keeper.medals()
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == 'raid' and keeper.has_listener(user_msg, "help"):
                    # generate the raid list help page
                    view = keeper.raid(user_msg)
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == 'up' and keeper.has_listener(user_msg, "record-keeper"):
                    # updates a given stat
                    view = keeper.up(user_msg)
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif (user_msg["cmd"].lower() == 'ls' and
                        (keeper.has_listener(user_msg, "record-keeper") or
                            keeper.has_listener(user_msg, "battle-keeper"))):
                    # lists stats for a given user
                    view = keeper.ls(user_msg)
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif (user_msg["cmd"].lower() == 'lb' and
                        (keeper.has_listener(user_msg, "record-keeper") or
                            keeper.has_listener(user_msg, "battle-keeper"))):
                    # creates a leaderboard for a given stat
                    view = keeper.lb(user_msg)
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == 'leagues' and keeper.has_listener(user_msg, "battle-keeper"):
                    # creates the medal list help page
                    view = keeper.leagues()
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == 'add-player' and keeper.has_listener(user_msg, "deletable-data"):
                    # manually add player to track player outside discord
                    view = keeper.add_player(user_msg)
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == 'uuid' and keeper.has_listener(user_msg, "deletable-data"):
                    # generate uuid(s) table
                    view = keeper.uuid(user_msg)
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == 'del' and keeper.has_listener(user_msg, "deletable-data"):
                    # delete a data point based a (medal, uuid) pair
                    view = keeper.delete(user_msg)
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == 'pvp' and keeper.has_listener(user_msg, "battle-keeper"):
                    # handles pvp win / lose
                    view = keeper.pvp(user_msg)
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == 'want' and keeper.has_listener(user_msg, "trade-keeper"):
                    # adds wanted pokemon to tradeboard
                    view = keeper.want(user_msg)
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == 'unwant' and keeper.has_listener(user_msg, "trade-keeper"):
                    # delete unwanted pokemon from tradeboard
                    view = keeper.unwant(user_msg)
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == 'tbu' and keeper.has_listener(user_msg, "trade-keeper"):
                    # list tradeboard by user
                    view = keeper.tbu(user_msg)
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == 'tbs' and keeper.has_listener(user_msg, "trade-keeper"):
                    # generates a search string for a user
                    # xxx hmm...
                    view = keeper.tbs(user_msg)
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == 'tbp' and keeper.has_listener(user_msg, "trade-keeper"):
                    # generates a tradeboard for a given pokemon
                    view = keeper.tbp(user_msg)
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif ((user_msg["cmd"].lower() == 'add-friend' or user_msg["cmd"].lower() == 'auf') and
                        keeper.has_listener(user_msg, "friend-keeper")):
                    # add friend to friends list
                    view = keeper.addfriend(user_msg)
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif ((user_msg["cmd"].lower() == 'remove-friend' or user_msg["cmd"].lower() == 'ruf') and
                        keeper.has_listener(user_msg, "friend-keeper")):
                    # remove friend from friends list
                    view = keeper.removefriend(user_msg)
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "friends" and keeper.has_listener(user_msg, "friend-keeper"):
                    # list friends friends list
                    view = keeper.list_friends(user_msg)
                    await send_message(view, dm_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == 'online' and keeper.has_listener(user_msg, "friend-keeper"):
                    # set status to online
                    view = keeper.online(user_msg)
                    await send_message(view, dm_message, user_msg, 30, edit=True)
                elif user_msg["cmd"].lower() == 'offline' and keeper.has_listener(user_msg, "friend-keeper"):
                    # set status to offline
                    view = keeper.offline(user_msg)
                    await send_message(view, dm_message, user_msg, 30, edit=True)
                elif ((user_msg["cmd"].lower() == 'ping-friends' or user_msg["cmd"].lower() == 'ltb') and
                        keeper.has_listener(user_msg, "friend-keeper")):
                    # ping friends user is looking for match
                    view = keeper.ping_friends(user_msg)
                    await send_message(view, dm_message, user_msg, 3600)
                elif ((user_msg["cmd"].lower() == 'rankgreat' or user_msg["cmd"].lower() == 'rank' or
                        user_msg["cmd"].lower() == 'rankg') and keeper.has_listener(user_msg, "iv-ranker") and
                        (str(client.user.id) == '588364227396239361' or
                            str(client.user.id) == '491321676835848203')):
                    view = keeper.rank(user_msg, "great")
                    await send_message(view, dm_message, user_msg, 120)
                elif ((user_msg["cmd"].lower() == 'rankultra' or user_msg["cmd"].lower() == 'ranku') and
                        keeper.has_listener(user_msg, "iv-ranker") and
                        (str(client.user.id) == '588364227396239361' or str(client.user.id) == '491321676835848203')):
                    view = keeper.rank(user_msg, "ultra")
                    await send_message(view, dm_message, user_msg, 120)
                elif ((user_msg["cmd"].lower() == 'rankmaster' or user_msg["cmd"].lower() == 'rankm') and
                        keeper.has_listener(user_msg, "iv-ranker") and
                        (str(client.user.id) == '588364227396239361' or str(client.user.id) == '491321676835848203')):
                    view = keeper.rank(user_msg, "master")
                    await send_message(view, dm_message, user_msg, 120)
                elif user_msg["cmd"].lower() == 'stats' and str(user_msg["raw_msg"].author.id) == '204058877317218304':
                    checkpoint_two = False
                    view = keeper.stats(user_msg)
                    await send_message(view, dm_message, user_msg, 300)
                elif (user_msg["cmd"].lower() == 'servers' and
                        str(user_msg["raw_msg"].author.id) == '204058877317218304'):
                    checkpoint_two = False
                    view = keeper.servers(user_msg)
                    await send_message(view, dm_message, user_msg, 300)
                elif user_msg["cmd"].lower() == 'roll' or user_msg["cmd"].lower() == 'd20':
                    # allow for global commands
                    pass
                else:
                    if keeper.has_listener(user_msg, "training-wheels") and checkpoint_two:
                        view = "Bidoof, sorry, something went wrong, try !help for more info"
                        await send_message(view, dm_message, user_msg, 30)

            # global_command
            if ((user_msg["cmd"].lower() == 'roll' or user_msg["cmd"].lower() == 'd20') and
                    keeper.has_listener(user_msg, "dice")):
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
    client.run(settings["bot_settings"][bot_environment]["discord_token"])
