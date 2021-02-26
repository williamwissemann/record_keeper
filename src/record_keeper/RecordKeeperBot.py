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

from record_keeper import BOT
from record_keeper.bot.module.admin.relay import AdminRelay
from record_keeper.utilities.message import parser


@BOT.client.event
async def on_ready():
    """ executed when discord client is connected """
    try:
        logging.info("signed in as: " + BOT.client.user.name)
        logging.info("with client id: " + str(BOT.client.user.id))
        logging.info("Discord.py Version: {}".format(discord.__version__))
    except Exception as e:
        logging.error(e, exc_info=True)


async def send_message(view, direct_message, cmd_msg, delete_time, edit=False):
    if view:
        if not isinstance(view, list):
            view = [view]

        cleanup = BOT.keeper.has_listener(cmd_msg, "message-cleanup")

        for msg in view:
            if edit:
                update_message = await cmd_msg["raw_msg"].channel.send("updating...")
                if cleanup and not direct_message:
                    await update_message.edit(content=msg, delete_after=delete_time)
                else:
                    await update_message.edit(content=msg)
            else:
                if cleanup and not direct_message:
                    await cmd_msg["raw_msg"].channel.send(msg, delete_after=delete_time)
                else:
                    await cmd_msg["raw_msg"].channel.send(msg)

        if BOT.keeper.has_listener(cmd_msg, "message-cleanup") and not direct_message:
            await cmd_msg["raw_msg"].delete()


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
        cmd_msg = parser(message.content)

        await AdminRelay().relay(message, cmd_msg, direct_message)

        """
        logging.info(cmd_msg)

        if cmd_msg:
            checkpoint_two = True
            if cmd_msg == "spacing issue":
                await message.channel.send(
                    "You're missing a space somewhere in the command"
                )

            if cmd_msg and not cmd_msg == "spacing issue":
                cmd_msg["raw_msg"] = message
                cmd_msg["client"] = BOT.client
                bot_msg = None

                # apply alises
                if len(cmd_msg["args"]) > 0:
                    cmd_msg["args"][0] = (
                        cmd_msg["args"][0].lower().replace("mmr", "gblelo")
                    )
                    cmd_msg["args"][0] = (
                        cmd_msg["args"][0].lower().replace("fisher", "fisherman")
                    )
                    cmd_msg["args"][0] = (
                        cmd_msg["args"][0].lower().replace("railstaff", "depotagent")
                    )

                if cmd_msg["cmd"].lower() == "donate":
                    view = BOT.keeper.helpDonateLink()
                    await send_message(view, direct_message, cmd_msg, 120, edit=True)
                elif cmd_msg["cmd"].lower() == "help" and BOT.keeper.has_listener(
                    cmd_msg, "help"
                ):
                    # creates the help page
                    view = BOT.keeper.help(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 120, edit=True)
                elif cmd_msg["cmd"].lower() == "medals" and BOT.keeper.has_listener(
                    cmd_msg, "help"
                ):
                    # creates the medal list help page
                    view = BOT.keeper.medals()
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "raid" and BOT.keeper.has_listener(
                    cmd_msg, "help"
                ):
                    # generate the raid list help page
                    view = BOT.keeper.raid(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "up" and BOT.keeper.has_listener(
                    cmd_msg, "record-keeper"
                ):
                    # updates a given stat
                    view = BOT.keeper.up(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "ls" and (
                    BOT.keeper.has_listener(cmd_msg, "record-keeper")
                    or BOT.keeper.has_listener(cmd_msg, "battle-keeper")
                ):
                    # lists stats for a given user
                    view = BOT.keeper.ls(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "lb" and (
                    BOT.keeper.has_listener(cmd_msg, "record-keeper")
                    or BOT.keeper.has_listener(cmd_msg, "battle-keeper")
                ):
                    # creates a leaderboard for a given stat
                    view = BOT.keeper.lb(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "leagues" and BOT.keeper.has_listener(
                    cmd_msg, "battle-keeper"
                ):
                    # creates the medal list help page
                    view = BOT.keeper.leagues()
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg[
                    "cmd"
                ].lower() == "add-player" and BOT.keeper.has_listener(
                    cmd_msg, "deletable-data"
                ):
                    # manually add player to track player outside discord
                    view = BOT.keeper.add_player(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "uuid" and BOT.keeper.has_listener(
                    cmd_msg, "deletable-data"
                ):
                    # generate uuid(s) table
                    view = BOT.keeper.uuid(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "del" and BOT.keeper.has_listener(
                    cmd_msg, "deletable-data"
                ):
                    # delete a data point based a (medal, uuid) pair
                    view = BOT.keeper.delete(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "pvp" and BOT.keeper.has_listener(
                    cmd_msg, "battle-keeper"
                ):
                    # handles pvp win / lose
                    view = BOT.keeper.pvp(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "want" and BOT.keeper.has_listener(
                    cmd_msg, "trade-keeper"
                ):
                    # adds wanted pokemon to tradeboard
                    view = BOT.keeper.want(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "unwant" and BOT.keeper.has_listener(
                    cmd_msg, "trade-keeper"
                ):
                    # delete unwanted pokemon from tradeboard
                    view = BOT.keeper.unwant(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "tbu" and BOT.keeper.has_listener(
                    cmd_msg, "trade-keeper"
                ):
                    # list tradeboard by user
                    view = BOT.keeper.tbu(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "tbs" and BOT.keeper.has_listener(
                    cmd_msg, "trade-keeper"
                ):
                    # generates a search string for a user
                    view = BOT.keeper.tbs(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "tbp" and BOT.keeper.has_listener(
                    cmd_msg, "trade-keeper"
                ):
                    # generates a tradeboard for a given pokemon
                    view = BOT.keeper.tbp(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "special" and BOT.keeper.has_listener(
                    cmd_msg, "trade-keeper"
                ):
                    # adds wanted pokemon to tradeboard
                    view = BOT.keeper.want(cmd_msg, board="SPECIAL_TRADE_BOARD")
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "unspecial" and BOT.keeper.has_listener(
                    cmd_msg, "trade-keeper"
                ):
                    # delete unwanted pokemon from tradeboard
                    view = BOT.keeper.unwant(cmd_msg, board="SPECIAL_TRADE_BOARD")
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "stbu" and BOT.keeper.has_listener(
                    cmd_msg, "trade-keeper"
                ):
                    # list tradeboard by user
                    view = BOT.keeper.tbu(cmd_msg, board="SPECIAL_TRADE_BOARD")
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "stbs" and BOT.keeper.has_listener(
                    cmd_msg, "trade-keeper"
                ):
                    # generates a search string for a user
                    view = BOT.keeper.tbs(cmd_msg, board="SPECIAL_TRADE_BOARD")
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "stbp" and BOT.keeper.has_listener(
                    cmd_msg, "trade-keeper"
                ):
                    # generates a tradeboard for a given pokemon
                    view = BOT.keeper.tbp(cmd_msg, board="SPECIAL_TRADE_BOARD")
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif (
                    cmd_msg["cmd"].lower() == "add-friend"
                    or cmd_msg["cmd"].lower() == "auf"
                ) and BOT.keeper.has_listener(cmd_msg, "friend-keeper"):
                    # add friend to friends list
                    view = BOT.keeper.addfriend(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif (
                    cmd_msg["cmd"].lower() == "remove-friend"
                    or cmd_msg["cmd"].lower() == "ruf"
                ) and BOT.keeper.has_listener(cmd_msg, "friend-keeper"):
                    # remove friend from friends list
                    view = BOT.keeper.removefriend(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "friends" and BOT.keeper.has_listener(
                    cmd_msg, "friend-keeper"
                ):
                    # list friends friends list
                    view = BOT.keeper.list_friends(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 90, edit=True)
                elif cmd_msg["cmd"].lower() == "online" and BOT.keeper.has_listener(
                    cmd_msg, "friend-keeper"
                ):
                    # set status to online
                    view = BOT.keeper.online(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 30, edit=True)
                elif cmd_msg["cmd"].lower() == "offline" and BOT.keeper.has_listener(
                    cmd_msg, "friend-keeper"
                ):
                    # set status to offline
                    view = BOT.keeper.offline(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 30, edit=True)
                elif (
                    cmd_msg["cmd"].lower() == "ping-friends"
                    or cmd_msg["cmd"].lower() == "ltb"
                ) and BOT.keeper.has_listener(cmd_msg, "friend-keeper"):
                    # ping friends user is looking for match
                    view = BOT.keeper.ping_friends(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 3600)
                elif (
                    (
                        cmd_msg["cmd"].lower() == "rankgreat"
                        or cmd_msg["cmd"].lower() == "rank"
                        or cmd_msg["cmd"].lower() == "rankg"
                    )
                    and BOT.keeper.has_listener(cmd_msg, "iv-ranker")
                    and (
                        str(BOT.client.user.id) == "588364227396239361"
                        or str(BOT.client.user.id) == "491321676835848203"
                    )
                ):
                    view = BOT.keeper.rank(cmd_msg, "great")
                    await send_message(view, direct_message, cmd_msg, 120)
                elif (
                    (
                        cmd_msg["cmd"].lower() == "rankultra"
                        or cmd_msg["cmd"].lower() == "ranku"
                    )
                    and BOT.keeper.has_listener(cmd_msg, "iv-ranker")
                    and (
                        str(BOT.client.user.id) == "588364227396239361"
                        or str(BOT.client.user.id) == "491321676835848203"
                    )
                ):
                    view = BOT.keeper.rank(cmd_msg, "ultra")
                    await send_message(view, direct_message, cmd_msg, 120)
                elif (
                    (
                        cmd_msg["cmd"].lower() == "rankmaster"
                        or cmd_msg["cmd"].lower() == "rankm"
                    )
                    and BOT.keeper.has_listener(cmd_msg, "iv-ranker")
                    and (
                        str(BOT.client.user.id) == "588364227396239361"
                        or str(BOT.client.user.id) == "491321676835848203"
                    )
                ):
                    view = BOT.keeper.rank(cmd_msg, "master")
                    await send_message(view, direct_message, cmd_msg, 120)
                elif (
                    cmd_msg["cmd"].lower() == "stats"
                    and str(cmd_msg["raw_msg"].author.id) == "204058877317218304"
                ):
                    checkpoint_two = False
                    view = BOT.keeper.stats(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 300)
                elif (
                    cmd_msg["cmd"].lower() == "servers"
                    and str(cmd_msg["raw_msg"].author.id) == "204058877317218304"
                ):
                    checkpoint_two = False
                    view = BOT.keeper.servers(cmd_msg)
                    await send_message(view, direct_message, cmd_msg, 300)
                elif (
                    cmd_msg["cmd"].lower() == "roll"
                    or cmd_msg["cmd"].lower() == "d20"
                ):
                    # allow for global commands
                    pass
                else:
                    if (
                        BOT.keeper.has_listener(cmd_msg, "training-wheels")
                        and checkpoint_two
                    ):
                        view = "Bidoof, sorry, something went wrong, try !help for more info"
                        await send_message(view, direct_message, cmd_msg, 30)

            # global_command
            if (
                cmd_msg["cmd"].lower() == "roll" or cmd_msg["cmd"].lower() == "d20"
            ) and BOT.keeper.has_listener(cmd_msg, "dice"):

                update_message = await message.channel.send("rolling...")
                # dice rolls d6
                await asyncio.sleep(2)
                if len(cmd_msg["args"]) > 0:
                    counter = random.randint(1, int(cmd_msg["args"][0]))
                elif cmd_msg["cmd"].lower() == "d20":
                    counter = random.randint(1, 20)
                else:
                    counter = random.randint(1, 6)
                bot_msg = "{} rolled a {}".format(message.author.name, counter)
                await update_message.edit(content=bot_msg)
            """


if __name__ == "__main__":
    BOT.client.run(BOT.discord_token)
