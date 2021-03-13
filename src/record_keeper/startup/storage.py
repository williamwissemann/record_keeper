import logging

from record_keeper import BOT
from record_keeper.startup.query import (
    create_table_if_not_exist,
    drop_tables,
    get_all_tables,
)


class Storage:
    """Validates the database is created with the expected tables"""

    def __init__(self):
        """Initializes list to validate against"""
        self.table_names = []
        self.accepted_tables = []
        self.basic_tables = []
        self.badge_tables = []
        self.type_tables = []

        self.custom_tables = []

        self.pokemonByNumber = {}
        self.pokemonByName = {}

        self.__build_pokemon_list__

        self.__verify_database__
        self.__delete_unused_tables__

    @property
    def __build_pokemon_list__(self):
        """Creates  validation  with the pokemon"""
        for pokemon in BOT.schema["pokemon"]["names"]:
            invalid_symbols = [".", " ", "_", "'"]
            pokeclean = pokemon
            for symbol in invalid_symbols:
                pokeclean = pokeclean.replace(symbol, "")
            number = BOT.schema["pokemon"]["names"][pokemon]
            self.pokemonByNumber[number] = pokeclean
            self.pokemonByName[pokeclean] = number

    @property
    def __verify_database__(self):
        """Creates any table found in the schema not in the database."""
        tables = BOT.schema.get("tables")
        for category in tables:
            table_category = tables.get(category)
            for table_name in table_category.get("table_names"):
                for init in table_category.get("table"):
                    table_value = table_category["table"][init]
                    sql = table_value.get("sql")
                    accepted = table_value.get("accepted")
                    name = table_name + init.replace("init", "")

                    self.table_names.append(name)
                    if accepted:
                        self.accepted_tables.append(name)
                    elif category == "basic_tables":
                        self.basic_tables.append(name)
                    elif category == "badge_tables":
                        self.badge_tables.append(name)
                    elif category == "type_tables":
                        self.type_tables.append(name)
                    elif category == "custom_tables":
                        self.custom_tables.append(name)

                    logging.info(f"create_table_if_not_exist {name}")
                    create_table_if_not_exist(name, sql)

    @property
    def __delete_unused_tables__(self):
        """Removes any table not found in the schema from the database."""
        for name in get_all_tables():
            name = name[0]
            if name not in self.table_names:
                logging.info(f"dropping {name}")
                drop_tables(name)
