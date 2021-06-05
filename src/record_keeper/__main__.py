import logging

import discord

from . import BOT
from .module.about.relay import BotInfo
from .module.admin.relay import AdminRelay
from .module.help.relay import HelpRelay
from .module.pvp_iv.relay import IVRelay
from .module.random.relay import RandomRelay
from .module.record_keeper.relay import RecordRelay
from .module.trade_keeper.relay import TradeRelay
from .module.training_wheels.relay import TrainingWheels
from .utilities.message import MessageWrapper


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
    """Executed on discord message reaction add event"""
    pass


@BOT.client.event
async def on_raw_reaction_remove(payload):
    """Executed on discord message reaction remove event"""
    pass


@BOT.client.event
async def on_message(message):
    """Executed on discord message event"""
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