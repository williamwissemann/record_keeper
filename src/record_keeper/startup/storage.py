import logging

from record_keeper import BOT
from record_keeper.startup.query import (
    create_table_if_not_exist,
    drop_tables,
    get_all_tables,
)


class Storage:
    def __init__(self):
        self.table_names = []
        self.accepted_tables = []
        self.basic_tables = []
        self.badge_tables = []
        self.type_tables = []

        self.custom_tables = []

        self.pokemonByNumber = {}
        self.pokemonByName = {}

        schema = BOT.schema
        self.verify_database(schema["tables"])

        # deal with the pokemon
        for pokemon in schema["pokemon"]["names"]:
            invalid_symbols = [".", " ", "_", "'"]
            pokeclean = pokemon
            for symbol in invalid_symbols:
                pokeclean = pokeclean.replace(symbol, "")
            number = schema["pokemon"]["names"][pokemon]
            self.pokemonByNumber[number] = pokeclean
            self.pokemonByName[pokeclean] = number

    def verify_database(self, tables):
        """
        Initialize a table if it doesn't already exist
        """
        for category in tables:
            table_category = tables.get(category)
            for table_name in table_category["table_names"]:
                for init in table_category["table"]:
                    table_value = table_category["table"][init]
                    sql = table_value["sql"]
                    accepted = table_value["accepted"]
                    name = table_name + init.replace("init", "")

                    self.table_names.append(name)
                    if accepted:
                        self.accepted_tables.append(name)
                    if category == "basic_tables":
                        self.basic_tables.append(name)
                    if category == "badge_tables":
                        self.badge_tables.append(name)
                    if category == "type_tables":
                        self.type_tables.append(name)
                    if category == "custom_tables":
                        self.custom_tables.append(name)

                    logging.info(f"create_table_if_not_exist {name}")
                    create_table_if_not_exist(name, sql)

        # drop tables that are not being used
        for name in get_all_tables():
            name = name[0]
            if name not in self.table_names:
                logging.info(f"dropping {name}")
                drop_tables(name)
