
import sqlite3
import datetime
import uuid
import json
import os
import shutil
import re


class UserStats:
    """
        Handles the database manipulation
    """
    def __init__(self, database_name="test.db", version='0.0'):
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
        # load the DB
        self.conn = sqlite3.connect(database_name)
        self.c = self.conn.cursor()

        # Check if we need to migrate database to a new format
        if os.path.isfile(database_name) and version != "IGNORE_VERSION":
            try:
                cdbv = self.database_version()[0][0]
            except:
                cdbv = "0.0"

            if cdbv != version and version != "IGNORE_VERSION":
                self.conn.close()
                name = re.findall("/database/(.*).db",  database_name)[0]
                backup_name = "/database/{}_backup_{}.db".format(name, cdbv)
                backup_name = re.sub("/database/(.*)", backup_name, database_name)
                if not os.path.isfile(backup_name):
                    shutil.copyfile(database_name, backup_name)
                else:
                    print("WARNING: database backup already exists!")
                os.remove(database_name)
                self.conn = sqlite3.connect(database_name)
                self.c = self.conn.cursor()
                self.init_table(data["tables"])
                self.migrate(backup_name, cdbv, version)
                cdbv = self.database_version()[0][0]
                assert str(cdbv) == str(version)
            else:
                self.init_table(data["tables"])
        else:
            self.init_table(data["tables"])

        print("loading complete")

    def init_table(self, tables):
        """
        Initilize a table if it doesn't already exist
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
                    if category == "pvp_leagues" and "_elo" not in name and "_ties" not in name:
                        self.pvp_leagues.append(name)
                    self.c.execute("CREATE TABLE IF NOT EXISTS " + name + " " + sql)

    def get_decorator(func):
        """
        The get decorator:
            sql string -> database [SELECT] -> return array
        """
        def wrapper(self, *args, **kwargs):
            sql_string = func(self, *args, **kwargs)
            recent = []
            for row in self.c.execute(sql_string):
                recent.append(row)
            return recent
        return wrapper

    def update_decorator(func):
        """
        The get decorator
            sql string -> database [INSERT/REPLACE/UPDATE/DELETE]
        """
        def wrapper(self, *args, **kwargs):
            sql_string = func(self, *args, **kwargs)
            self.c.execute(sql_string)
            self.conn.commit()
        return wrapper

    @get_decorator
    def database_version(self):
        return str("SELECT info FROM botinfo WHERE field = 'version'")

    @get_decorator
    def list_gamertag(self, server):
        return str("SELECT * FROM gamertag WHERE server_id = '" + str(server) + "' ORDER BY gamertag")

    @get_decorator
    def get_recent(self, server, table, user, limit=25, uuid=False):
        sql = "SELECT * FROM " + str(table)
        sql += " WHERE gamertag = '" + str(user) + "'"
        if not server == "ViaDirectMessage":
            sql += " AND ( server_id = '" + str(server) + "' OR server_id = 'ViaDirectMessage')"
        if uuid:
            sql += " AND update_at >= datetime('now', '-1 day') "
            sql += " AND update_at <= datetime('now', '+1 day') "
        sql += " ORDER BY update_at DESC"
        sql += " LIMIT " + str(limit)
        return sql

    @get_decorator
    def get_recent_pvp(self, server, table, user, limit=25, uuid=False):
        sql = "SELECT * FROM " + str(table)
        sql += " WHERE gamertag_winner = '" + str(user) + "'"
        sql += " OR gamertag_loser = '" + str(user) + "'"
        if not server == "ViaDirectMessage":
            sql += " AND ( server_id = '" + str(server) + "' OR server_id = 'ViaDirectMessage')"
        if uuid:
            sql += " AND update_at >= datetime('now', '-1 day') "
            sql += " AND update_at <= datetime('now', '+1 day') "
        sql += " ORDER BY update_at DESC"
        sql += " LIMIT " + (str(limit))
        return sql

    @get_decorator
    def get_recent_pvp_no_limit(self, server, table):
        sql = "SELECT * FROM " + str(table)
        if not server == "ViaDirectMessage":
            sql += " WHERE ( server_id = '" + str(server) + "' OR server_id = 'ViaDirectMessage')"
        sql += " ORDER BY update_at ASC"
        return sql

    @get_decorator
    def get_elo_leaders(self, server, table):
        sql = "SELECT * FROM " + str(table)
        sql += " ORDER BY elo DESC"
        return sql

    @get_decorator
    def get_trade_board_by_user(self, server, user):
        sql = "SELECT * FROM TRADE_BOARD"
        sql += " WHERE gamertag = '" + str(user) + "'"
        if not server == "ViaDirectMessage":
            sql += " AND ( server_id = '" + str(server) + "' OR server_id = 'ViaDirectMessage')"
        sql += " ORDER BY number ASC"
        return sql

    @get_decorator
    def get_trade_board_by_pokemon(self, server, pokemon):
        sql = "SELECT * FROM TRADE_BOARD"
        sql += " WHERE pokemon = '" + str(pokemon) + "'"
        if not server == "ViaDirectMessage":
            sql += " AND ( server_id = '" + str(server) + "' OR server_id = 'ViaDirectMessage')"
        sql += " ORDER BY number ASC"
        return sql

    @get_decorator
    def get_leaders(self, server, table):
        if str(table) == "Stardust":
            sql = "SELECT uuid, server_id, update_at, gamertag, value, note FROM " + str(table)
            if not server == "ViaDirectMessage":
                sql += " WHERE ( server_id = '" + str(server) + "' OR server_id = 'ViaDirectMessage')"
            sql += " GROUP BY gamertag"
            sql += " ORDER BY value DESC, update_at ASC"
            sql += " LIMIT 25"
        else:
            sql = "SELECT uuid, server_id, update_at, gamertag, MAX(value), note FROM " + str(table)
            if not server == "ViaDirectMessage":
                sql += " WHERE ( server_id = '" + str(server) + "' OR server_id = 'ViaDirectMessage')"
            sql += " GROUP BY gamertag"
            sql += " ORDER BY value DESC, update_at ASC"
            sql += " LIMIT 25"
        return sql

    @update_decorator
    def update_medal(self, server, table, gamertag, value, update_at, notes=""):
        float(value)
        update_at.replace(" ", "T")
        id = uuid.uuid4()
        sql = str(
            "INSERT INTO " + table +
            " values( " +
            "'" + str(id) + "'," +
            "'" + str(server) + "'," +
            "'" + str(update_at) + "'," +
            "'" + str(gamertag) + "'," +
            "'" + str(value) + "'," +
            "'" + str(notes) + "')")
        return sql

    @update_decorator
    def update_elo(self, server, table, uuid, elo_winner, elo_winner_change, elo_loser, elo_loser_change):
        sql = str(
            "UPDATE " + str(table) +
            " SET elo_winner = '" + str(elo_winner) +
            "', elo_winner_change = '" + str(elo_winner_change) +
            "', elo_loser = '" + str(elo_loser) +
            "', elo_loser_change='" + str(elo_loser_change) + "'" +
            ", server_id='" + str(server) + "'" +
            " WHERE uuid = '" + str(uuid) + "'" +
            " AND server_id = '" + str(server) + "'")
        print(sql)
        return sql

    @update_decorator
    def update_elo_player(self, table, gamertag, elo):
        sql = str(
            "REPLACE INTO " + str(table) +
            " VALUES (" +
            "'" + str(gamertag) + "'," +
            "'" + str(elo) + "')")
        print(sql)
        return sql

    @update_decorator
    def update_pvp(self, server, table, gamertag, gamertag_winner, gamertag_loser, update_at, tie, notes=""):
        update_at.replace(" ", "T")
        id = uuid.uuid4()
        sql = str(
            "INSERT INTO " + table +
            " VALUES( " +
            "'" + str(id) + "'," +
            "'" + str(server) + "'," +
            "'" + str(update_at) + "'," +
            "'" + str(gamertag) + "'," +
            "'" + str(gamertag_winner) + "'," +
            "'" + str(-1) + "'," +
            "'" + str(-1) + "'," +
            "'" + str(gamertag_loser) + "'," +
            "'" + str(-1) + "'," +
            "'" + str(-1) + "'," +
            "'" + str(tie) + "'," +
            "'" + str(notes) + "')")
        return sql

    @update_decorator
    def update_trade_board(self, server, PokemonNumber, PokemonName, user, notes=""):
        id = uuid.uuid4()
        sql = str(
            "INSERT OR REPLACE INTO TRADE_BOARD" +
            " VALUES( " +
            "'" + str(id) + "'," +
            "'" + str(server) + "'," +
            "'" + str(user) + "'," +
            "'" + str(PokemonName) + "'," +
            "'" + str(PokemonNumber) + "'," +
            "'" + str(notes) + "')")
        return sql

    @update_decorator
    def delete_row(self, server, table, user, uuid):
        sql = "DELETE FROM " + str(table)
        sql += " WHERE gamertag = '" + str(user) + "'"
        if not server == "ViaDirectMessage":
            sql += " AND ( server_id = '" + str(server) + "' OR server_id = 'ViaDirectMessage')"
        sql += " AND update_at >= datetime('now', '-1 day') "
        sql += " AND update_at <= datetime('now','+1 day') "
        sql += " AND uuid = '" + str(uuid) + "'"
        return sql

    @update_decorator
    def delete_from_trade_board(self, server, PokemonName, user):
        sql = "DELETE FROM TRADE_BOARD"
        sql += " WHERE gamertag = '" + str(user) + "'"
        if not server == "ViaDirectMessage":
            sql += " AND ( server_id = '" + str(server) + "' OR server_id = 'ViaDirectMessage')"
        sql += "AND pokemon = '" + str(PokemonName) + "'"
        return sql

    def add_gamertag(self, server, gamertag):
        if not self.gamertag_exists(gamertag):
            self.c.execute("""INSERT INTO gamertag values ('""" + server + """, """ + gamertag + """')""")
            self.conn.commit()
            return True
        return False

    def gamertag_exists(self, server,  gamertag):
        self.c.execute("SELECT * FROM gamertag WHERE gamertag=? AND server_id = '" + str(server) + "'", (gamertag,))
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
            sql += " AND ( server_id = '" + str(server) + "' OR server_id = 'ViaDirectMessage')"
        sql += " AND update_at >= datetime('now', '-" + str(days) + " days')"
        sql += " AND update_at <= datetime('now','+1 day')"
        sql += " ORDER BY update_at ASC"
        for row in self.c.execute(sql):
            total = row[0]

        wins = 0
        sql = "SELECT COUNT(gamertag_winner) FROM " + str(table)
        sql += " WHERE gamertag_winner = '" + str(user) + "'"
        if not server == "ViaDirectMessage":
            sql += " AND ( server_id = '" + str(server) + "' OR server_id = 'ViaDirectMessage')"
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
            sql_string += " AND ( server_id = '" + str(server) + "' OR server_id = 'ViaDirectMessage')"
        sql_string += " AND update_at >= datetime('now', '-" + str(days) + " days') "
        sql_string += " AND update_at <=  datetime('now','+1 day') "
        sql_string += " ORDER BY update_at ASC"

        recent = []
        average_increase = []
        for row in self.c.execute(sql_string):
            recent.append(row)
            if len(recent) > 1:
                average_increase.append(
                    recent[len(recent) - 1][4] - recent[len(recent) - 2][4])
            else:
                continue

        if len(recent) > 0:
            y, m, d = recent[0][2].split("T")[0].split(" ")[0].split("-")
            min_date = datetime.datetime(int(y), int(m), int(d))
            y, m, d = recent[(len(recent) - 1)][2].split("T")[0].split(" ")[0].split("-")
            max_date = datetime.datetime(int(y), int(m), int(d))
            day_diff = (max_date - min_date).days + 1
            return float(sum(average_increase)) / day_diff
        return 0.0

    @update_decorator
    def update_friend_board(self, server, gamertag1, gamertag2):
        id = uuid.uuid4()
        sql = str(
            "INSERT OR REPLACE INTO FRIEND_BOARD" +
            " VALUES( " +
            "'" + str(id) + "'," +
            "'" + str(server) + "'," +
            "'" + str(gamertag1) + "'," +
            "'" + str(gamertag2) + "')")
        return sql

    @update_decorator
    def delete_from_friend_board(self, server, gamertag1, gamertag2):
        sql = "DELETE FROM FRIEND_BOARD"
        sql += " WHERE gamertag1 = '" + str(gamertag1) + "'"
        sql += " AND gamertag2 = '" + str(gamertag2) + "'"
        return sql

    @get_decorator
    def get_friends(self, server, gamertag, limit=1000):
        sql = "SELECT DISTINCT gamertag2, IFNULL(status, 'Offline') as status "
        sql += " FROM FRIEND_BOARD "
        sql += " LEFT JOIN ACTIVE_BOARD "
        sql += " ON gamertag2 = gamertag "
        sql += " WHERE gamertag1 = '" + str(gamertag) + "'"
        sql += " ORDER BY status DESC, gamertag2 ASC"
        sql += " LIMIT " + str(limit)
        return sql

    @get_decorator
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

    @update_decorator
    def update_active_board(self, server, gamertag, status):
        id = uuid.uuid4()
        sql = str(
            "INSERT OR REPLACE INTO ACTIVE_BOARD" +
            " VALUES( " +
            "'" + str(id) + "'," +
            "'" + str(gamertag) + "'," +
            "'" + str(status) + "')")
        return sql

    @get_decorator
    def get_listeners(self, server, channel):
        sql = "SELECT * FROM listener "
        if not server == "ViaDirectMessage":
            sql += " WHERE server_id = '" + str(server) + "'"
            sql += " AND active_channel = '" + str(channel) + "'"
        return sql

    @get_decorator
    def has_listeners(self, server, channel, toggle):
        sql = str(
            "SELECT * FROM listener " +
            " WHERE server_id = '" + str(server) + "'" +
            " AND toggle = '" + str(toggle) + "'" +
            " AND active_channel = '" + str(channel) + "'")
        return sql

    @update_decorator
    def update_listener(self, server, channel, toggle):
        id = uuid.uuid4()
        sql = str(
            "INSERT or IGNORE INTO listener " +
            " values( " +
            "'" + str(id) + "'," +
            "'" + str(server) + "'," +
            "'" + str(toggle) + "'," +
            "'" + str(channel) + "')")
        return sql

    @update_decorator
    def remove_listener(self, server, channel, toggle):
        sql = str(
            "DELETE FROM listener " +
            " WHERE server_id = '" + str(server) +
            "' AND" +
            " active_channel = '" + str(channel) +
            "' AND" +
            " toggle = '" + str(toggle) + "'")
        return sql

    def migrate(self, backup_name, cdbv, version):
        old_conn = sqlite3.connect(backup_name)
        old_c = old_conn.cursor()

        if str(version) == "1.0" and str(cdbv) == "0.0":
            server_id = "487986792868478987"
        elif str(version) == "1.0.1" and str(cdbv) == "0.0":
            server_id = "513857416983609354"
        else:
            assert False

        print("ADDING server_id: {}".format(server_id))
        array = []
        for table in old_c.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            array.append(table[0])

        for table in array:
            for row in old_c.execute("SELECT * FROM " + table):
                sql = str(
                    "INSERT INTO " + table +
                    " values( ")
                for eln in range(len(row)):
                    sql += "'" + str(row[eln]) + "',"
                    if eln == 0 and not table == 'ACTIVE_BOARD' and "_elo" not in table:
                        sql += "'" + str(server_id) + "',"
                sql = sql[0:len(sql)-2] + "')"
                self.c.execute(sql)

        id = uuid.uuid4()
        sql = str(
            "INSERT OR REPLACE INTO botinfo" +
            " VALUES( " +
            "'" + str(id) + "'," +
            "'version'," +
            "'" + str(version) + "')")
        self.c.execute(sql)
        self.conn.commit()

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
    d.update_medal("DepotAgent", "test_account", 10, datetime.datetime.now().isoformat())
    d.update_medal("DepotAgent", "test_account", 15, datetime.datetime.now().isoformat())
    d.update_medal("DepotAgent", "test_account", 25, datetime.datetime.now().isoformat())
    print()
    # d.list_medal("DepotAgent")
    print()
    for x in d.get_recent("DepotAgent", "test_account"):
        print(x)
