import logging

import discord

from record_keeper import BOT
from record_keeper.module.about.relay import BotInfo
from record_keeper.module.admin.relay import AdminRelay
from record_keeper.module.help.relay import HelpRelay
from record_keeper.module.pvp_iv.relay import IVRelay
from record_keeper.module.random.relay import RandomRelay
from record_keeper.module.record_keeper.relay import RecordRelay
from record_keeper.module.trade_keeper.relay import TradeRelay
from record_keeper.module.training_wheels.relay import TrainingWheels
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
async def on_raw_reaction_add(payload):
    pass


@BOT.client.event
async def on_raw_reaction_remove(payload):
    pass


@BOT.client.event
async def on_message(message):
    # build context of the message
    msg = MessageWrapper(message)

    if msg.failure:
        await msg.send_message(msg.failure, 600)
        return None
    elif not msg.in_scope:
        return None

    relays = [
        BotInfo(),
        HelpRelay(),
        AdminRelay(),
        RecordRelay(),
        TradeRelay(),
        IVRelay(),
        RandomRelay(),
        TrainingWheels(),
    ]

    for relay in relays:
        response = await relay.relay(msg)
        if response:
            return response

    return None


if __name__ == "__main__":
    BOT.client.run(BOT.discord_token)
