"""A package to help keep game stats via discord."""

import importlib.metadata
import logging

from record_keeper.bot.startup.setup import BotSetup

__version__ = importlib.metadata.version("record-keeper")

# create the BOT object with initial values
try:
    BOT = BotSetup()
    logging.info("checking the database is in a good state")
except Exception:
    logging.error("failure to initialize the bot", stack_info=True)

# validate & fix the database so it has the correct structure
try:
    from record_keeper.bot.startup.validator import Validator
    CHECK = Validator()
except Exception:
    logging.error("failure run validator", stack_info=True)
