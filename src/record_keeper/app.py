import logging

import discord

from record_keeper import BOT
from record_keeper.module.admin.relay import AdminRelay
from record_keeper.module.help.relay import HelpRelay
from record_keeper.module.record_keeper.relay import RecordRelay
from record_keeper.utilities.message import MessageWrapper


@BOT.client.event
async def on_ready():
    """Executed when discord client is connected"""
    try:
        logging.info("signed in as: " + BOT.client.user.name)
        logging.info("with client id: " + str(BOT.client.user.id))
        logging.info("Discord.py Version: {}".format(discord.__version__))
    except Exception as e:
        logging.error(e, exc_info=True)


@BOT.client.event
async def on_message(message):
    # build context of the message
    msg = MessageWrapper(message)

    if msg.failure:
        await msg.send_message(msg.failure, 600)
        return
    elif not msg.in_scope:
        return

    if await HelpRelay().relay(msg):
        return

    if await AdminRelay().relay(msg):
        return

    if await RecordRelay().relay(msg):
        return

    """
    if await TradeRelay().relay(msg):
        return

    if await IVRelay().relay(msg):
        return

    if await RandomRelay().relay(msg):
        return

    # await TradeRelay().relay(msg)
    # await IVRelay().relay(msg)
    # await RandomRelay().relay(msg)
    """

    """
    if (BOT.keeper.has_listener(cmd_msg, "training-wheels"):
    view = "Bidoof, something went wrong, try !help for more info"
    await send_message(view, direct_message, cmd_msg, 30)
    """

if __name__ == "__main__":
    BOT.client.run(BOT.discord_token)
