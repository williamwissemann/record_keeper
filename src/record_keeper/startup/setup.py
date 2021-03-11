import json
import logging
import os

import discord

from record_keeper.utilities.sqlite3_wrapper import Sqlite3Wrapper
from record_keeper.utilities.bypass import DecoratorBypass
import sys

class BotSetup:
    def __init__(self):
        # CONSTANT for help messages
        self.HELP_PROMPT = "Bidoof, something went wrong, try !help for info"

        # setup a logger
        format_template = "%(levelname)s %(filename)s:%(lineno)d %(message)s"
        logging.basicConfig(format=format_template)
        logging.root.level = logging.INFO

        # discover some paths
        abs_path = os.path.abspath(__file__)
        rel_path = os.path.relpath(__file__)
        base_name = os.path.basename(__file__)
        config_file = base_name.replace(".py", ".json")
        exec_path = abs_path.replace(rel_path, "")
        logging.info(f"exec_path: {exec_path}")

        # Load in json file to initialize the tables in the database
        schema_path = os.path.join(exec_path, "config", "schema.json")
        logging.info(f"found schema_path @ {schema_path}")
        with open(schema_path) as f:
            self.schema = json.load(f)

        test_mode = ("pytest" in sys.argv[0])
        if test_mode:
            self.environment = "testing"
            self.database = Sqlite3Wrapper("test.db")
            self.client = DecoratorBypass()
            return

        # load data out of the configuration file
        config_file = os.path.join(exec_path, "config", config_file)
        logging.info(f"found config_file @ {config_file}")
        with open(config_file) as f:
            settings = json.load(f)
            bot_settings = settings.get("bot_settings")
            self.environment = bot_settings["environment"]
            environment_settings = bot_settings[self.environment]
            self.discord_token = environment_settings["discord_token"]

        # load sqlite3 database
        database_file = environment_settings["database"]
        path_to_database = os.path.join(exec_path, "database", database_file)
        logging.info(f"loading the database @ {path_to_database}")
        self.database = Sqlite3Wrapper(path_to_database)

        # create the discord client
        logging.info(f"logging in to discord {path_to_database}")
        intents = discord.Intents.default()
        intents.presences = True
        intents.members = True
        self.client = discord.Client(max_messages=100000, intents=intents)
