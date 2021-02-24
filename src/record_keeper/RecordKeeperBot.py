import asyncio
import datetime
import json
import logging
import math
import os
import random
import sys
import time

import discord

import record_keeper.RecordKeeperViews as bot_message
from record_keeper import BOT
from record_keeper.RecordKeeperFunc import RecordKeeper
from record_keeper.RecordKeeperUtils import message_parser


@BOT.client.event
async def on_ready():
    """ executed when discord client is connected """
    try:
        logging.info("signed in as: " + BOT.client.user.name)
        logging.info("with client id: " + str(BOT.client.user.id))
        logging.info("Discord.py Version: {}".format(discord.__version__))
    except Exception as e:
        logging.error(e, exc_info=True)


async def send_message(view, direct_message, user_msg, delete_time, edit=False):
    if view:
        if not isinstance(view, list):
            view = [view]

        cleanup = BOT.keeper.has_listener(user_msg, "message-cleanup")

        for msg in view:
            if edit:
                update_message = await user_msg["raw_msg"].channel.send("updating...")
                if cleanup and not direct_message:
                    await update_message.edit(content=msg, delete_after=delete_time)
                else:
                    await update_message.edit(content=msg)
            else:
                if cleanup and not direct_message:
                    await user_msg["raw_msg"].channel.send(
                        msg, delete_after=delete_time
                    )
                else:
                    await user_msg["raw_msg"].channel.send(msg)

        if BOT.keeper.has_listener(user_msg, "message-cleanup") and not direct_message:
            await user_msg["raw_msg"].delete()


@BOT.client.event
async def on_message(message):
    checkpoint_one = False
    direct_message = False

    if "Direct Message" in str(message.channel):
        checkpoint_one = True
        direct_message = True
    if BOT.environment == "development" and "-testing" not in str(message.channel):
        logging.info("(dev) ignore message because of misisng '-testing' flag")
    elif BOT.environment == "production" and "-testing" in str(message.channel):
        logging.info("(prod) ignore message because of '-testing' flag")
    else:
        checkpoint_one = True

    if checkpoint_one and not message.author.bot:
        user_msg = message_parser(message.content)
        logging.info(user_msg)

        if user_msg:
            checkpoint_two = True
            if user_msg == "spacing issue":
                await message.channel.send(
                    "You're missing a space somewhere in the command"
                )
            if not direct_message and message.author.guild_permissions.administrator:
                user_msg["raw_msg"] = message
                user_msg["client"] = BOT.client
                if user_msg["cmd"].lower() == "setup":
                    checkpoint_two = False
                    await message.channel.send(
                        BOT.keeper.setup(user_msg), delete_after=600
                    )
                    if not direct_message:
                        await message.delete()
                elif user_msg["cmd"].lower() == "activate":
                    checkpoint_two = False
                    if len(user_msg["args"]) > 0:
                        await message.channel.send(
                            BOT.keeper.activate(user_msg), delete_after=60
                        )
                        if not direct_message:
                            await message.delete()
                elif user_msg["cmd"].lower() == "deactivate":
                    checkpoint_two = False
                    await message.channel.send(
                        BOT.keeper.deactivate(user_msg), delete_after=60
                    )
                    if not direct_message:
                        await message.delete()
                elif user_msg["cmd"].lower() == "active":
                    checkpoint_two = False
                    await message.channel.send(
                        BOT.keeper.list_listener(user_msg), delete_after=90
                    )
                    if not direct_message:
                        await message.delete()
            if user_msg and not user_msg == "spacing issue":
                user_msg["raw_msg"] = message
                user_msg["client"] = BOT.client
                bot_msg = None

                # apply alises
                if len(user_msg["args"]) > 0:
                    user_msg["args"][0] = (
                        user_msg["args"][0].lower().replace("mmr", "gblelo")
                    )
                    user_msg["args"][0] = (
                        user_msg["args"][0].lower().replace("fisher", "fisherman")
                    )
                    user_msg["args"][0] = (
                        user_msg["args"][0].lower().replace("railstaff", "depotagent")
                    )

                if user_msg["cmd"].lower() == "donate":
                    view = BOT.keeper.helpDonateLink()
                    await send_message(view, direct_message, user_msg, 120, edit=True)
                elif user_msg["cmd"].lower() == "help" and BOT.keeper.has_listener(
                    user_msg, "help"
                ):
                    # creates the help page
                    view = BOT.keeper.help(user_msg)
                    await send_message(view, direct_message, user_msg, 120, edit=True)
                elif user_msg["cmd"].lower() == "medals" and BOT.keeper.has_listener(
                    user_msg, "help"
                ):
                    # creates the medal list help page
                    view = BOT.keeper.medals()
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "raid" and BOT.keeper.has_listener(
                    user_msg, "help"
                ):
                    # generate the raid list help page
                    view = BOT.keeper.raid(user_msg)
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "up" and BOT.keeper.has_listener(
                    user_msg, "record-keeper"
                ):
                    # updates a given stat
                    view = BOT.keeper.up(user_msg)
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "ls" and (
                    BOT.keeper.has_listener(user_msg, "record-keeper")
                    or BOT.keeper.has_listener(user_msg, "battle-keeper")
                ):
                    # lists stats for a given user
                    view = BOT.keeper.ls(user_msg)
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "lb" and (
                    BOT.keeper.has_listener(user_msg, "record-keeper")
                    or BOT.keeper.has_listener(user_msg, "battle-keeper")
                ):
                    # creates a leaderboard for a given stat
                    view = BOT.keeper.lb(user_msg)
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "leagues" and BOT.keeper.has_listener(
                    user_msg, "battle-keeper"
                ):
                    # creates the medal list help page
                    view = BOT.keeper.leagues()
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg[
                    "cmd"
                ].lower() == "add-player" and BOT.keeper.has_listener(
                    user_msg, "deletable-data"
                ):
                    # manually add player to track player outside discord
                    view = BOT.keeper.add_player(user_msg)
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "uuid" and BOT.keeper.has_listener(
                    user_msg, "deletable-data"
                ):
                    # generate uuid(s) table
                    view = BOT.keeper.uuid(user_msg)
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "del" and BOT.keeper.has_listener(
                    user_msg, "deletable-data"
                ):
                    # delete a data point based a (medal, uuid) pair
                    view = BOT.keeper.delete(user_msg)
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "pvp" and BOT.keeper.has_listener(
                    user_msg, "battle-keeper"
                ):
                    # handles pvp win / lose
                    view = BOT.keeper.pvp(user_msg)
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "want" and BOT.keeper.has_listener(
                    user_msg, "trade-keeper"
                ):
                    # adds wanted pokemon to tradeboard
                    view = BOT.keeper.want(user_msg)
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "unwant" and BOT.keeper.has_listener(
                    user_msg, "trade-keeper"
                ):
                    # delete unwanted pokemon from tradeboard
                    view = BOT.keeper.unwant(user_msg)
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "tbu" and BOT.keeper.has_listener(
                    user_msg, "trade-keeper"
                ):
                    # list tradeboard by user
                    view = BOT.keeper.tbu(user_msg)
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "tbs" and BOT.keeper.has_listener(
                    user_msg, "trade-keeper"
                ):
                    # generates a search string for a user
                    view = BOT.keeper.tbs(user_msg)
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "tbp" and BOT.keeper.has_listener(
                    user_msg, "trade-keeper"
                ):
                    # generates a tradeboard for a given pokemon
                    view = BOT.keeper.tbp(user_msg)
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "special" and BOT.keeper.has_listener(
                    user_msg, "trade-keeper"
                ):
                    # adds wanted pokemon to tradeboard
                    view = BOT.keeper.want(user_msg, board="SPECIAL_TRADE_BOARD")
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "unspecial" and BOT.keeper.has_listener(
                    user_msg, "trade-keeper"
                ):
                    # delete unwanted pokemon from tradeboard
                    view = BOT.keeper.unwant(user_msg, board="SPECIAL_TRADE_BOARD")
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "stbu" and BOT.keeper.has_listener(
                    user_msg, "trade-keeper"
                ):
                    # list tradeboard by user
                    view = BOT.keeper.tbu(user_msg, board="SPECIAL_TRADE_BOARD")
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "stbs" and BOT.keeper.has_listener(
                    user_msg, "trade-keeper"
                ):
                    # generates a search string for a user
                    view = BOT.keeper.tbs(user_msg, board="SPECIAL_TRADE_BOARD")
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "stbp" and BOT.keeper.has_listener(
                    user_msg, "trade-keeper"
                ):
                    # generates a tradeboard for a given pokemon
                    view = BOT.keeper.tbp(user_msg, board="SPECIAL_TRADE_BOARD")
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif (
                    user_msg["cmd"].lower() == "add-friend"
                    or user_msg["cmd"].lower() == "auf"
                ) and BOT.keeper.has_listener(user_msg, "friend-keeper"):
                    # add friend to friends list
                    view = BOT.keeper.addfriend(user_msg)
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif (
                    user_msg["cmd"].lower() == "remove-friend"
                    or user_msg["cmd"].lower() == "ruf"
                ) and BOT.keeper.has_listener(user_msg, "friend-keeper"):
                    # remove friend from friends list
                    view = BOT.keeper.removefriend(user_msg)
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "friends" and BOT.keeper.has_listener(
                    user_msg, "friend-keeper"
                ):
                    # list friends friends list
                    view = BOT.keeper.list_friends(user_msg)
                    await send_message(view, direct_message, user_msg, 90, edit=True)
                elif user_msg["cmd"].lower() == "online" and BOT.keeper.has_listener(
                    user_msg, "friend-keeper"
                ):
                    # set status to online
                    view = BOT.keeper.online(user_msg)
                    await send_message(view, direct_message, user_msg, 30, edit=True)
                elif user_msg["cmd"].lower() == "offline" and BOT.keeper.has_listener(
                    user_msg, "friend-keeper"
                ):
                    # set status to offline
                    view = BOT.keeper.offline(user_msg)
                    await send_message(view, direct_message, user_msg, 30, edit=True)
                elif (
                    user_msg["cmd"].lower() == "ping-friends"
                    or user_msg["cmd"].lower() == "ltb"
                ) and BOT.keeper.has_listener(user_msg, "friend-keeper"):
                    # ping friends user is looking for match
                    view = BOT.keeper.ping_friends(user_msg)
                    await send_message(view, direct_message, user_msg, 3600)
                elif (
                    (
                        user_msg["cmd"].lower() == "rankgreat"
                        or user_msg["cmd"].lower() == "rank"
                        or user_msg["cmd"].lower() == "rankg"
                    )
                    and BOT.keeper.has_listener(user_msg, "iv-ranker")
                    and (
                        str(BOT.client.user.id) == "588364227396239361"
                        or str(BOT.client.user.id) == "491321676835848203"
                    )
                ):
                    view = BOT.keeper.rank(user_msg, "great")
                    await send_message(view, direct_message, user_msg, 120)
                elif (
                    (
                        user_msg["cmd"].lower() == "rankultra"
                        or user_msg["cmd"].lower() == "ranku"
                    )
                    and BOT.keeper.has_listener(user_msg, "iv-ranker")
                    and (
                        str(BOT.client.user.id) == "588364227396239361"
                        or str(BOT.client.user.id) == "491321676835848203"
                    )
                ):
                    view = BOT.keeper.rank(user_msg, "ultra")
                    await send_message(view, direct_message, user_msg, 120)
                elif (
                    (
                        user_msg["cmd"].lower() == "rankmaster"
                        or user_msg["cmd"].lower() == "rankm"
                    )
                    and BOT.keeper.has_listener(user_msg, "iv-ranker")
                    and (
                        str(BOT.client.user.id) == "588364227396239361"
                        or str(BOT.client.user.id) == "491321676835848203"
                    )
                ):
                    view = BOT.keeper.rank(user_msg, "master")
                    await send_message(view, direct_message, user_msg, 120)
                elif (
                    user_msg["cmd"].lower() == "stats"
                    and str(user_msg["raw_msg"].author.id) == "204058877317218304"
                ):
                    checkpoint_two = False
                    view = BOT.keeper.stats(user_msg)
                    await send_message(view, direct_message, user_msg, 300)
                elif (
                    user_msg["cmd"].lower() == "servers"
                    and str(user_msg["raw_msg"].author.id) == "204058877317218304"
                ):
                    checkpoint_two = False
                    view = BOT.keeper.servers(user_msg)
                    await send_message(view, direct_message, user_msg, 300)
                elif (
                    user_msg["cmd"].lower() == "roll"
                    or user_msg["cmd"].lower() == "d20"
                ):
                    # allow for global commands
                    pass
                else:
                    if (
                        BOT.keeper.has_listener(user_msg, "training-wheels")
                        and checkpoint_two
                    ):
                        view = "Bidoof, sorry, something went wrong, try !help for more info"
                        await send_message(view, direct_message, user_msg, 30)

            # global_command
            if (
                user_msg["cmd"].lower() == "roll" or user_msg["cmd"].lower() == "d20"
            ) and BOT.keeper.has_listener(user_msg, "dice"):

                update_message = await message.channel.send("rolling...")
                # dice rolls d6
                await asyncio.sleep(2)
                if len(user_msg["args"]) > 0:
                    counter = random.randint(1, int(user_msg["args"][0]))
                elif user_msg["cmd"].lower() == "d20":
                    counter = random.randint(1, 20)
                else:
                    counter = random.randint(1, 6)
                bot_msg = "{} rolled a {}".format(message.author.name, counter)
                await update_message.edit(content=bot_msg)


if __name__ == "__main__":
    BOT.client.run(BOT.discord_token)
