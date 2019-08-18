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
                    await message.channel.send(keeper.list_listener(user_msg),
                        delete_after=90)
                    if not dm_message:
                        await message.delete()
                elif user_msg["cmd"].lower() == 'setup':
                    checkpoint_two = False
                    await message.channel.send("wip setup", delete_after=60)
                    if not dm_message:
                        await message.delete()
            if user_msg and not user_msg == "spacing issue":
                user_msg["raw_msg"] = message
                user_msg["client"] = client
                bot_msg = None
                if user_msg["cmd"].lower() == 'donate':
                    await message.channel.send(keeper.helpDonateLink())
                elif user_msg["cmd"].lower() == 'help' and keeper.has_listener(user_msg, "help"):
                    # creates the help page
                    msg = keeper.help(user_msg)
                    if isinstance(msg, list):
                        for x in msg:
                            if not dm_message:
                                await message.channel.send(x, delete_after=90)
                            else:
                                await message.channel.send(x)
                    if not dm_message:
                        await message.delete()
                elif user_msg["cmd"].lower() == 'medals' and keeper.has_listener(user_msg, "help"):
                    # creates the medal list help page
                    await message.channel.send(keeper.medals())
                elif user_msg["cmd"].lower() == 'raid' and keeper.has_listener(user_msg, "help"):
                    # generate the raid list help page
                    await message.channel.send(keeper.raid(user_msg))
                elif user_msg["cmd"].lower() == 'up' and keeper.has_listener(user_msg, "record-keeper"):
                    # updates a given stat
                    await message.channel.send(keeper.up(user_msg))
                elif (user_msg["cmd"].lower() == 'ls' and (keeper.has_listener(user_msg, "record-keeper") or keeper.has_listener(user_msg, "battle-keeper"))):
                    # lists stats for a given user
                    await message.channel.send(keeper.ls(user_msg))
                elif (user_msg["cmd"].lower() == 'lb' and
                    (keeper.has_listener(user_msg, "record-keeper") or keeper.has_listener(user_msg, "battle-keeper"))):
                    # creates a leaderboard for a given stat
                    await message.channel.send(keeper.lb(user_msg))
                elif user_msg["cmd"].lower() == 'add-player' and keeper.has_listener(user_msg, "deletable-data"):
                    # manually add player to track player outside discord
                    await message.channel.send(keeper.add_player(user_msg))
                elif user_msg["cmd"].lower() == 'uuid' and keeper.has_listener(user_msg, "deletable-data"):
                    # generate uuid(s) table
                    await message.channel.send(keeper.uuid(user_msg))
                elif user_msg["cmd"].lower() == 'del' and keeper.has_listener(user_msg, "deletable-data"):
                    # delete a data point based a (medal, uuid) pair
                    await message.channel.send(keeper.delete(user_msg))
                elif user_msg["cmd"].lower() == 'pvp' and keeper.has_listener(user_msg, "battle-keeper"):
                    # handles pvp win / lose
                    await message.channel.send(keeper.pvp(user_msg))
                elif user_msg["cmd"].lower() == 'want' and keeper.has_listener(user_msg, "trade-keeper"):
                    # adds wanted pokemon to tradeboard
                    await message.channel.send(keeper.want(user_msg))
                elif user_msg["cmd"].lower() == 'unwant' and keeper.has_listener(user_msg, "trade-keeper"):
                    # delete unwanted pokemon from tradeboard
                    await message.channel.send(keeper.unwant(user_msg))
                elif user_msg["cmd"].lower() == 'tbu' and keeper.has_listener(user_msg, "trade-keeper"):
                    # list tradeboard by user
                    await message.channel.send(keeper.tbu(user_msg))
                elif user_msg["cmd"].lower() == 'tbs' and keeper.has_listener(user_msg, "trade-keeper"):
                    # generates a search string for a user
                    await message.channel.send(keeper.tbs(user_msg))
                elif user_msg["cmd"].lower() == 'tbp' and keeper.has_listener(user_msg, "trade-keeper"):
                    # generates a tradeboard for a given pokemon
                    await message.channel.send(keeper.tbp(user_msg))
                elif ((user_msg["cmd"].lower() == 'add-friend' or user_msg["cmd"].lower() == 'auf') and
                    keeper.has_listener(user_msg, "friend-keeper")):
                    # add friend to friends list
                    update_message = await message.channel.send("updating...")
                    await update_message.edit(content=keeper.addfriend(user_msg),
                                            delete_after=90)
                    if not dm_message:
                        await message.delete()
                elif ((user_msg["cmd"].lower() == 'remove-friend' or user_msg["cmd"].lower() == 'ruf') and
                    keeper.has_listener(user_msg, "friend-keeper")):
                    # remove friend from friends list
                    update_message = await message.channel.send("updating...")
                    await update_message.edit(content=keeper.removefriend(user_msg),
                                            delete_after=90)
                    if not dm_message:
                        await message.delete()
                elif user_msg["cmd"].lower() == "friends" and keeper.has_listener(user_msg, "friend-keeper"):
                    # list friends friends list
                    view = keeper.list_friends(user_msg)
                    if isinstance(view, list):
                        for x in view:
                            await message.channel.send(x, delete_after=90)
                    else:
                        await message.channel.send(view, delete_after=90)
                    if not dm_message:
                        await message.delete()
                elif user_msg["cmd"].lower() == 'online' and keeper.has_listener(user_msg, "friend-keeper"):
                    # set status to online
                    await message.channel.send(keeper.online(user_msg),
                                            delete_after=30)
                    if not dm_message:
                        await message.delete()
                elif user_msg["cmd"].lower() == 'offline' and keeper.has_listener(user_msg, "friend-keeper"):
                    # set status to offline
                    await message.channel.send(keeper.offline(user_msg),
                                            delete_after=30)
                    if not dm_message:
                        await message.delete()
                elif ((user_msg["cmd"].lower() == 'ping-friends' or user_msg["cmd"].lower() == 'ltb') and
                        keeper.has_listener(user_msg, "friend-keeper")):
                    # ping friends user is looking for match
                    view = keeper.ping_friends(user_msg)
                    if isinstance(view, list):
                        for x in view:
                            await message.channel.send(x, delete_after=3600)
                    else:
                        await message.channel.send(view, delete_after=3600)
                    if not dm_message:
                        await message.delete()
                elif ((user_msg["cmd"].lower() == 'rankgreat' or user_msg["cmd"].lower() == 'rank' or
                    user_msg["cmd"].lower() == 'rankg') and keeper.has_listener(user_msg, "iv-ranker") and
                    (str(client.user.id) == '588364227396239361' or str(client.user.id) == '491321676835848203')):
                    # ping looks up pokemons pvp rank
                    await message.channel.send(keeper.rank(user_msg, "great"))
                elif ((user_msg["cmd"].lower() == 'rankultra' or
                    user_msg["cmd"].lower() == 'ranku') and keeper.has_listener(user_msg, "iv-ranker") and
                    (str(client.user.id) == '588364227396239361' or str(client.user.id) == '491321676835848203')):
                    # ping looks up pokemons pvp rank
                    await message.channel.send(keeper.rank(user_msg, "ultra"))
                elif ((user_msg["cmd"].lower() == 'rankmaster' or
                    user_msg["cmd"].lower() == 'rankm') and keeper.has_listener(user_msg, "iv-ranker") and
                    (str(client.user.id) == '588364227396239361' or str(client.user.id) == '491321676835848203')):
                    # ping looks up pokemons pvp rank
                    await message.channel.send(keeper.rank(user_msg, "master"))
                elif user_msg["cmd"].lower() == 'roll' or user_msg["cmd"].lower() == 'd20':
                    # allow for global commands
                    pass
                else:
                    if keeper.has_listener(user_msg, "training-wheels") and checkpoint_two:
                        try:
                            await update_message.edit(
                                content="Bidoof, sorry, something went wrong, try !help for more info", delete_after=30)
                        except:
                            await message.channel.send("Bidoof, sorry, something went wrong, try !help for more info",
                                                    delete_after=30)
                    if keeper.has_listener(user_msg, "delete-messages") and not dm_message :
                        await message.delete()

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
