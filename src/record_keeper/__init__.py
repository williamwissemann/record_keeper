"""A package to help keep game stats via discord."""

import importlib.metadata
import logging

from record_keeper.bot.setup import BotSetup

__version__ = importlib.metadata.version("record-keeper")

try:
    BOT = BotSetup()
except Exception:
    logging.error("failure to initialize the bot", stack_info=True)
