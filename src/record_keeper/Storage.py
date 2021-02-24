import datetime
import json
import os
import re
import shutil
import sqlite3
import uuid

from record_keeper import BOT


class UserStats:
    """
    Handles the database manipulation
    """

    def __init__(self):
        # setup table catagories
        print("loading_database...")
        self.accepted_tables = []
        self.basic_tables = []
        self.badge_tables = []
        self.type_tables = []
        self.custom_tables = []
        self.raid_tables = []
        self.pvp_leagues = []
        self.pokemonByNumber = {}
        self.pokemonByName = {}
        # Load in json file to initialize the tables in the database
        path = os.path.realpath(__file__).rstrip(".py")
        with open(path + ".json") as f:
            data = json.load(f)
        # deal with the pokemon
        for pokemon in data["pokemon"]["names"]:
            pokeclean = pokemon
            pokeclean = pokeclean.replace(".", "")
            pokeclean = pokeclean.replace(" ", "")
            pokeclean = pokeclean.replace("-", "")
            pokeclean = pokeclean.replace("'", "")
            number = data["pokemon"]["names"][pokemon]
            self.pokemonByNumber[number] = pokeclean
            self.pokemonByName[pokeclean] = number
            data["tables"]["raid_tables"]["table_names"][pokeclean] = pokemon
            data["tables"]["raid_tables"]["table_names"][pokeclean + "N"] = pokemon
            data["tables"]["raid_tables"]["table_names"][pokeclean + "BB"] = pokemon
            data["tables"]["raid_tables"]["table_names"][pokeclean + "CB"] = pokemon
        for pokemon in data["pokemon"]["variants"]["Alolan"]:
            pokeclean = "A" + pokemon
            data["tables"]["raid_tables"]["table_names"][pokeclean] = pokemon
            data["tables"]["raid_tables"]["table_names"][pokeclean + "N"] = pokemon
            data["tables"]["raid_tables"]["table_names"][pokeclean + "BB"] = pokemon
            data["tables"]["raid_tables"]["table_names"][pokeclean + "CB"] = pokemon

        self.init_table(data["tables"])

        print("loading complete")

    def init_table(self, tables):
        """
        Initialize a table if it doesn't already exist
        """
        for category in tables:
            for table_name in tables[category]["table_names"]:
                for init in tables[category]["table"]:
                    sql = tables[category]["table"][init]["sql"]
                    accepted = tables[category]["table"][init]["accepted"]
                    name = table_name + init.replace("init", "")
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
                    if category == "raid_tables":
                        self.raid_tables.append(name)
                    if (
                        category == "pvp_leagues"
                        and "_elo" not in name
                        and "_ties" not in name
                    ):
                        self.pvp_leagues.append(name)

                    sql_str = f"CREATE TABLE IF NOT EXISTS {name} {sql}"
                    self.create_table_if_not_exist(create_table_if_not_exist)

    @BOT.database.update
    def create_table_if_not_exist(self, str):
        return "SELECT info FROM botinfo WHERE field = 'version'"

    @BOT.database.get
    def database_version(self) -> str:
        return "SELECT info FROM botinfo WHERE field = 'version'"

    @BOT.database.get
    def list_gamertag(self, server: str) -> str:
        server = str(server)
        sql_query = (
            f"SELECT * FROM gamertag WHERE server_id='{server}' ORDER BY gamertag"
        )

        return str(sql_query)

    @BOT.database.get
    def get_recent(
        self, server: str, table: str, user: str, limit: int = 25, uuid: bool = False
    ):
        sql = f"SELECT * FROM {str(table)}"
        sql += f" WHERE gamertag = f'{str(user)}'"
        if not server == "ViaDirectMessage":
            sql += (
                f" AND ( server_id = '{str(server)}' OR server_id = 'ViaDirectMessage')"
            )
        if uuid:
            sql += " AND update_at >= datetime('now', '-1 day') "
            sql += " AND update_at <= datetime('now', '+1 day') "
        sql += " ORDER BY update_at DESC"
        sql += " LIMIT " + str(limit)
        return sql

    @BOT.database.get
    def get_recent_pvp(self, server, table, user, limit=25, uuid=False):
        sql = "SELECT * FROM " + str(table)
        sql += " WHERE gamertag_winner = '" + str(user) + "'"
        sql += " OR gamertag_loser = '" + str(user) + "'"
        if not server == "ViaDirectMessage":
            sql += (
                " AND ( server_id = '"
                + str(server)
                + "' OR server_id = 'ViaDirectMessage')"
            )
        if uuid:
            sql += " AND update_at >= datetime('now', '-1 day') "
            sql += " AND update_at <= datetime('now', '+1 day') "
        sql += " ORDER BY update_at DESC"
        sql += " LIMIT " + (str(limit))
        return sql

    @BOT.database.get
    def get_recent_pvp_no_limit(self, server, table):
        sql = "SELECT * FROM " + str(table)
        if not server == "ViaDirectMessage":
            sql += (
                " WHERE ( server_id = '"
                + str(server)
                + "' OR server_id = 'ViaDirectMessage')"
            )
        sql += " ORDER BY update_at ASC"
        return sql

    @BOT.database.get
    def get_elo_leaders(self, server, table):
        sql = "SELECT * FROM " + str(table)
        sql += " ORDER BY elo DESC"
        return sql

    @BOT.database.get
    def get_trade_board_by_user(self, server, user, board):
        sql = f"SELECT * FROM {board}"
        sql += f" WHERE gamertag = '{str(user)}'"
        if not server == "ViaDirectMessage":
            sql += (
                " AND ( server_id = '"
                + str(server)
                + "' OR server_id = 'ViaDirectMessage')"
            )
        sql += " ORDER BY number ASC"
        return sql

    @BOT.database.get
    def get_trade_board_by_pokemon(self, server, pokemon, board):
        sql = f"SELECT * FROM {board}"
        sql += " WHERE pokemon = '" + str(pokemon) + "'"
        if not server == "ViaDirectMessage":
            sql += (
                " AND ( server_id = '"
                + str(server)
                + "' OR server_id = 'ViaDirectMessage')"
            )
        sql += " ORDER BY number ASC"
        return sql

    @BOT.database.get
    def get_leaders(self, server, table):
        if str(table) == "Stardust":
            sql = (
                "SELECT uuid, server_id, update_at, gamertag, value, note FROM "
                + str(table)
            )
            if not server == "ViaDirectMessage":
                sql += (
                    " WHERE ( server_id = '"
                    + str(server)
                    + "' OR server_id = 'ViaDirectMessage')"
                )
            sql += " GROUP BY gamertag"
            sql += " ORDER BY value DESC, update_at ASC"
            sql += " LIMIT 25"
        else:
            sql = (
                "SELECT uuid, server_id, update_at, gamertag, MAX(value), note FROM "
                + str(table)
            )
            if not server == "ViaDirectMessage":
                sql += (
                    " WHERE ( server_id = '"
                    + str(server)
                    + "' OR server_id = 'ViaDirectMessage')"
                )
            sql += " GROUP BY gamertag"
            sql += " ORDER BY value DESC, update_at ASC"
            sql += " LIMIT 25"
        return sql

    @BOT.database.update
    def update_medal(self, server, table, gamertag, value, update_at, notes=""):
        float(value)
        update_at.replace(" ", "T")
        id = uuid.uuid4()
        sql = str(
            "INSERT INTO "
            + table
            + " values( "
            + "'"
            + str(id)
            + "',"
            + "'"
            + str(server)
            + "',"
            + "'"
            + str(update_at)
            + "',"
            + "'"
            + str(gamertag)
            + "',"
            + "'"
            + str(value)
            + "',"
            + "'"
            + str(notes)
            + "')"
        )
        return sql

    @BOT.database.update
    def update_elo(
        self,
        server,
        table,
        uuid,
        elo_winner,
        elo_winner_change,
        elo_loser,
        elo_loser_change,
    ):
        sql = str(
            "UPDATE "
            + str(table)
            + " SET elo_winner = '"
            + str(elo_winner)
            + "', elo_winner_change = '"
            + str(elo_winner_change)
            + "', elo_loser = '"
            + str(elo_loser)
            + "', elo_loser_change='"
            + str(elo_loser_change)
            + "'"
            + ", server_id='"
            + str(server)
            + "'"
            + " WHERE uuid = '"
            + str(uuid)
            + "'"
            + " AND server_id = '"
            + str(server)
            + "'"
        )
        print(sql)
        return sql

    @BOT.database.update
    def update_elo_player(self, table, gamertag, elo):
        sql = str(
            "REPLACE INTO "
            + str(table)
            + " VALUES ("
            + "'"
            + str(gamertag)
            + "',"
            + "'"
            + str(elo)
            + "')"
        )
        print(sql)
        return sql

    @BOT.database.update
    def update_pvp(
        self,
        server,
        table,
        gamertag,
        gamertag_winner,
        gamertag_loser,
        update_at,
        tie,
        notes="",
    ):
        update_at.replace(" ", "T")
        id = uuid.uuid4()
        sql = str(
            "INSERT INTO "
            + table
            + " VALUES( "
            + "'"
            + str(id)
            + "',"
            + "'"
            + str(server)
            + "',"
            + "'"
            + str(update_at)
            + "',"
            + "'"
            + str(gamertag)
            + "',"
            + "'"
            + str(gamertag_winner)
            + "',"
            + "'"
            + str(-1)
            + "',"
            + "'"
            + str(-1)
            + "',"
            + "'"
            + str(gamertag_loser)
            + "',"
            + "'"
            + str(-1)
            + "',"
            + "'"
            + str(-1)
            + "',"
            + "'"
            + str(tie)
            + "',"
            + "'"
            + str(notes)
            + "')"
        )
        return sql

    @BOT.database.update
    def update_trade_board(
        self, server, PokemonNumber, PokemonName, user, notes="", board=""
    ):
        id = uuid.uuid4()
        sql = str(
            f"INSERT OR REPLACE INTO {board}"
            + " VALUES( "
            + "'"
            + str(id)
            + "',"
            + "'"
            + str(server)
            + "',"
            + "'"
            + str(user)
            + "',"
            + "'"
            + str(PokemonName)
            + "',"
            + "'"
            + str(PokemonNumber)
            + "',"
            + "'"
            + str(notes)
            + "')"
        )
        return sql

    @BOT.database.update
    def delete_row(self, server, table, user, uuid):
        sql = "DELETE FROM " + str(table)
        sql += " WHERE gamertag = '" + str(user) + "'"
        if not server == "ViaDirectMessage":
            sql += (
                " AND ( server_id = '"
                + str(server)
                + "' OR server_id = 'ViaDirectMessage')"
            )
        sql += " AND update_at >= datetime('now', '-1 day') "
        sql += " AND update_at <= datetime('now','+1 day') "
        sql += " AND uuid = '" + str(uuid) + "'"
        return sql

    @BOT.database.update
    def delete_from_trade_board(self, server, PokemonName, user, board):
        sql = f"DELETE FROM {board}"
        sql += " WHERE gamertag = '" + str(user) + "'"
        if not server == "ViaDirectMessage":
            sql += (
                " AND ( server_id = '"
                + str(server)
                + "' OR server_id = 'ViaDirectMessage')"
            )
        sql += "AND pokemon = '" + str(PokemonName) + "'"
        return sql

    def add_gamertag(self, server, gamertag):
        if not self.gamertag_exists(gamertag):
            self.c.execute(
                """INSERT INTO gamertag values ('"""
                + server
                + """, """
                + gamertag
                + """')"""
            )
            self.conn.commit()
            return True
        return False

    def gamertag_exists(self, server, gamertag):
        self.c.execute(
            "SELECT * FROM gamertag WHERE gamertag=? AND server_id = '"
            + str(server)
            + "'",
            (gamertag,),
        )
        if self.c.fetchone():
            return True
        else:
            return False

    def get_day_wl_avg(self, server, table, user, days=7):
        """ calculates w/l averages """
        total = 0
        sql = "SELECT COUNT(gamertag_winner) FROM " + str(table)
        sql += " WHERE gamertag_winner = '" + str(user) + "'"
        sql += " OR gamertag_loser = '" + str(user) + "'"
        if not server == "ViaDirectMessage":
            sql += (
                " AND ( server_id = '"
                + str(server)
                + "' OR server_id = 'ViaDirectMessage')"
            )
        sql += " AND update_at >= datetime('now', '-" + str(days) + " days')"
        sql += " AND update_at <= datetime('now','+1 day')"
        sql += " ORDER BY update_at ASC"
        for row in self.c.execute(sql):
            total = row[0]

        wins = 0
        sql = "SELECT COUNT(gamertag_winner) FROM " + str(table)
        sql += " WHERE gamertag_winner = '" + str(user) + "'"
        if not server == "ViaDirectMessage":
            sql += (
                " AND ( server_id = '"
                + str(server)
                + "' OR server_id = 'ViaDirectMessage')"
            )
        sql += " AND update_at >= datetime('now', '-" + str(days) + " days')"
        sql += " AND update_at <= datetime('now','+1 day')"
        sql += " AND tie == 0"
        sql += " ORDER BY update_at ASC"
        for row in self.c.execute(sql):
            wins = row[0]

        try:
            value = round(float(wins) / total, 3)
            return value
        except ZeroDivisionError:
            return 0.0

    def get_day_avg(self, server, table, user, days=7):
        """ calculates avreage based on number of days """
        sql_string = "SELECT * FROM " + str(table)
        sql_string += " WHERE gamertag = '" + str(user) + "'"
        if not server == "ViaDirectMessage":
            sql_string += (
                " AND ( server_id = '"
                + str(server)
                + "' OR server_id = 'ViaDirectMessage')"
            )
        sql_string += " AND update_at >= datetime('now', '-" + str(days) + " days') "
        sql_string += " AND update_at <=  datetime('now','+1 day') "
        sql_string += " ORDER BY update_at ASC"

        recent = []
        average_increase = []
        for row in self.c.execute(sql_string):
            recent.append(row)
            if len(recent) > 1:
                average_increase.append(
                    recent[len(recent) - 1][4] - recent[len(recent) - 2][4]
                )
            else:
                continue

        if len(recent) > 0:
            y, m, d = recent[0][2].split("T")[0].split(" ")[0].split("-")
            min_date = datetime.datetime(int(y), int(m), int(d))
            y, m, d = (
                recent[(len(recent) - 1)][2].split("T")[0].split(" ")[0].split("-")
            )
            max_date = datetime.datetime(int(y), int(m), int(d))
            day_diff = (max_date - min_date).days + 1
            return float(sum(average_increase)) / day_diff
        return 0.0

    @BOT.database.update
    def update_friend_board(self, server, gamertag1, gamertag2):
        id = uuid.uuid4()
        sql = str(
            "INSERT OR REPLACE INTO FRIEND_BOARD"
            + " VALUES( "
            + "'"
            + str(id)
            + "',"
            + "'"
            + str(server)
            + "',"
            + "'"
            + str(gamertag1)
            + "',"
            + "'"
            + str(gamertag2)
            + "')"
        )
        return sql

    @BOT.database.update
    def delete_from_friend_board(self, server, gamertag1, gamertag2):
        sql = "DELETE FROM FRIEND_BOARD"
        sql += " WHERE gamertag1 = '" + str(gamertag1) + "'"
        sql += " AND gamertag2 = '" + str(gamertag2) + "'"
        return sql

    @BOT.database.get
    def get_friends(self, server, gamertag, limit=1000):
        sql = "SELECT DISTINCT gamertag2, IFNULL(status, 'Offline') as status "
        sql += " FROM FRIEND_BOARD "
        sql += " LEFT JOIN ACTIVE_BOARD "
        sql += " ON gamertag2 = gamertag "
        sql += " WHERE gamertag1 = '" + str(gamertag) + "'"
        sql += " ORDER BY status DESC, gamertag2 ASC"
        sql += " LIMIT " + str(limit)
        return sql

    @BOT.database.get
    def get_online_friends(self, server, gamertag, limit=1000):
        sql = "SELECT DISTINCT gamertag2, IFNULL(status, 'Offline') as status "
        sql += " FROM FRIEND_BOARD "
        sql += " LEFT JOIN ACTIVE_BOARD "
        sql += " ON gamertag2 = gamertag "
        sql += " WHERE gamertag1 = '" + str(gamertag) + "'"
        sql += " AND status = 'Online' "
        sql += " ORDER BY status DESC, gamertag2 ASC"
        # sql += " LIMIT " + str(limit)
        return sql

    @BOT.database.update
    def update_active_board(self, server, gamertag, status):
        id = uuid.uuid4()
        sql = str(
            "INSERT OR REPLACE INTO ACTIVE_BOARD"
            + " VALUES( "
            + "'"
            + str(id)
            + "',"
            + "'"
            + str(gamertag)
            + "',"
            + "'"
            + str(status)
            + "')"
        )
        return sql

    @BOT.database.get
    def get_listeners(self, server, channel):
        sql = "SELECT * FROM listener "
        if not server == "ViaDirectMessage":
            sql += " WHERE server_id = '" + str(server) + "'"
            sql += " AND active_channel = '" + str(channel) + "'"
        return sql

    @BOT.database.get
    def has_listeners(self, server, channel, toggle):
        sql = str(
            "SELECT * FROM listener "
            + " WHERE server_id = '"
            + str(server)
            + "'"
            + " AND toggle = '"
            + str(toggle)
            + "'"
            + " AND active_channel = '"
            + str(channel)
            + "'"
        )
        return sql

    @BOT.database.update
    def update_listener(self, server, channel, toggle):
        id = uuid.uuid4()
        sql = str(
            "INSERT or IGNORE INTO listener "
            + " values( "
            + "'"
            + str(id)
            + "',"
            + "'"
            + str(server)
            + "',"
            + "'"
            + str(toggle)
            + "',"
            + "'"
            + str(channel)
            + "')"
        )
        return sql

    @BOT.database.update
    def remove_listener(self, server, channel, toggle):
        sql = str(
            "DELETE FROM listener "
            + " WHERE server_id = '"
            + str(server)
            + "' AND"
            + " active_channel = '"
            + str(channel)
            + "' AND"
            + " toggle = '"
            + str(toggle)
            + "'"
        )
        return sql


if __name__ == "__main__":
    # XXX Phase 2
    # replacing this junk with some Unit testing
    d = UserStats()
    d.add_gamertag("test_account")
    d.list_gamertag()
    print()
    print(d.gamertag_exists("random"))
    print(d.gamertag_exists("test_account"))
    print()
    d.update_medal("Kanto", "test_account", 151, datetime.datetime.now().isoformat())
    d.update_medal("Kanto", "doesnt_exist", 151, datetime.datetime.now().isoformat())
    d.update_medal(
        "DepotAgent", "test_account", 10, datetime.datetime.now().isoformat()
    )
    d.update_medal(
        "DepotAgent", "test_account", 15, datetime.datetime.now().isoformat()
    )
    d.update_medal(
        "DepotAgent", "test_account", 25, datetime.datetime.now().isoformat()
    )
    print()
    # d.list_medal("DepotAgent")
    print()
    for x in d.get_recent("DepotAgent", "test_account"):
        print(x)
