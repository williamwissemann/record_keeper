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

from record_keeper.utilities.sqlite3_wrapper import Sqlite3Wrapper


class BotSetup:
    def __init__(self):
        # setup a logger
        FORMAT = "%(levelname)s %(filename)s:%(lineno)d %(message)s"
        logging.basicConfig(format=FORMAT)
        logging.root.level = logging.INFO

        # discover some paths
        abs_path = os.path.abspath(__file__)
        rel_path = os.path.relpath(__file__)
        base_name = os.path.basename(__file__)
        config_file = base_name.replace(".py", ".json")
        exec_path = abs_path.replace(rel_path, "")

        # load data out of the configuration file
        config_file = os.path.join(exec_path, "config", config_file)
        with open(config_file) as f:
            settings = json.load(f)
            bot_settings = settings.get("bot_settings")
            self.environment = bot_settings["environment"]
            environment_settings = bot_settings[self.environment]
            dev_environment = bot_settings["development"]
            self.discord_token = environment_settings["discord_token"]

        # load sqlite3 database
        self.database_version = "1.0.2"
        database_file = environment_settings["database"]
        path_to_database = os.path.join(exec_path, "database", database_file)
        self.database = Sqlite3Wrapper(path_to_database)

        # create the discord client
        intents = discord.Intents.default()
        intents.presences = True
        intents.members = True
        self.client = discord.Client(max_messages=100000, intents=intents)
