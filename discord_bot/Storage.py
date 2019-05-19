
import sqlite3
import datetime
import uuid
import json
import os


class UserStats:
    """
        Handles the database manipulation
    """
    def __init__(self, database_name="test.db"):
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
    def list_gamertag(self):
        return str("SELECT * FROM gamertag ORDER BY gamertag")

    @get_decorator
    def get_recent(self, table, user, limit=25):
        sql = str(
            "SELECT * FROM " + str(table) +
            " WHERE gamertag = '" + str(user) + "'" +
            " ORDER BY update_at DESC" +
            " LIMIT " + str(limit))
        return sql

    @get_decorator
    def get_recent_pvp(self, table, user, limit=25):
        sql = str(
            "SELECT * FROM " + str(table) +
            " WHERE gamertag_winner = '" + str(user) + "'" +
            " OR gamertag_loser = '" + str(user) + "'" +
            " ORDER BY update_at DESC" +
            " LIMIT " + (str(limit)))
        return sql

    @get_decorator
    def get_recent_pvp_no_limit(self, table):
        sql = str(
            "SELECT * FROM " + str(table) +
            " ORDER BY update_at ASC")
        return sql

    @get_decorator
    def get_elo_leaders(self, table):
        sql = str(
            "SELECT * FROM " + str(table) +
            " ORDER BY elo DESC" +
            " LIMIT 25")
        return sql

    @get_decorator
    def get_trade_board_by_user(self, user):
        sql = str(
            "SELECT * FROM TRADE_BOARD" +
            " WHERE gamertag = '" + str(user) + "'" +
            " ORDER BY number ASC")
        return sql

    @get_decorator
    def get_trade_board_by_pokemon(self, pokemon):
        sql = str(
            "SELECT * FROM TRADE_BOARD" +
            " WHERE pokemon = '" + str(pokemon) + "'" +
            " ORDER BY number ASC")
        return sql

    @get_decorator
    def get_recent_pvp(self, table, user, limit=25):
        sql = str(
            "SELECT * FROM " + str(table) +
            " WHERE gamertag_winner = '" + str(user) + "'" +
            " OR gamertag_loser = '" + str(user) + "'" +
            " ORDER BY update_at DESC" +
            " LIMIT " + (str(limit)))
        return sql

    @get_decorator
    def get_leaders(self, table):
        if str(table) == "Stardust":
            sql = str(
                "SELECT uuid, update_at, gamertag, value, note FROM " + str(table) +
                " GROUP BY gamertag" +
                " ORDER BY value DESC, update_at ASC" +
                " LIMIT 25")
        else:
            sql = str(
                "SELECT uuid, update_at,gamertag,  MAX(value), note FROM " + str(table) +
                " GROUP BY gamertag" +
                " ORDER BY value DESC, update_at ASC" +
                " LIMIT 25")
        return sql

    @update_decorator
    def update_medal(self, table, gamertag, value, update_at, notes=""):
        float(value)
        update_at.replace(" ", "T")
        id = uuid.uuid4()
        sql = str(
            "INSERT INTO " + table +
            " values( " +
            "'" + str(id) + "'," +
            "'" + str(update_at) + "'," +
            "'" + str(gamertag) + "'," +
            "'" + str(value) + "'," +
            "'" + str(notes) + "')")
        return sql

    @update_decorator
    def update_elo(self, table, uuid, elo_winner, elo_winner_change, elo_loser, elo_loser_change):
        sql = str(
            "UPDATE " + str(table) +
            " SET elo_winner = '" + str(elo_winner) +
            "', elo_winner_change = '" + str(elo_winner_change) +
            "', elo_loser = '" + str(elo_loser) +
            "', elo_loser_change='" + str(elo_loser_change) + "'" +
            " WHERE uuid = '" + str(uuid) + "'")
        return sql

    @update_decorator
    def update_elo_player(self, table, gamertag, elo):
        sql = str(
            "REPLACE INTO " + str(table) +
            " VALUES (" +
            "'" + str(gamertag) + "'" +
            ",'" + str(elo) + "')")
        return sql

    @update_decorator
    def update_pvp(self, table, gamertag, gamertag_winner, gamertag_loser, update_at, tie, notes=""):
        update_at.replace(" ", "T")
        id = uuid.uuid4()
        sql = str(
            "INSERT INTO " + table +
            " VALUES( " +
            "'" + str(id) + "'," +
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
    def update_trade_board(self, PokemonNumber, PokemonName, user, notes=""):
        id = uuid.uuid4()
        sql = str(
            "INSERT OR REPLACE INTO TRADE_BOARD" +
            " VALUES( " +
            "'" + str(id) + "'," +
            "'" + str(user) + "'," +
            "'" + str(PokemonName) + "'," +
            "'" + str(PokemonNumber) + "'," +
            "'" + str(notes) + "')")
        return sql

    @update_decorator
    def delete_row(self, table, user, uuid):
        sql = str(
            "DELETE FROM " + str(table) +
            " WHERE gamertag = '" + str(user) +
            "' AND" +
            " uuid = '" + str(uuid) + "'")
        return sql

    @update_decorator
    def delete_from_trade_board(self, PokemonName, user):
        sql = str(
            "DELETE FROM TRADE_BOARD" +
            " WHERE gamertag = '" + str(user) + "' AND" +
            " pokemon = '" + str(PokemonName) + "'")
        return sql

    def add_gamertag(self, gamertag):
        if not self.gamertag_exists(gamertag):
            self.c.execute("""INSERT INTO gamertag values ('""" + gamertag + """')""")
            self.conn.commit()
            return True
        return False

    def gamertag_exists(self, gamertag):
        self.c.execute("SELECT * FROM gamertag WHERE gamertag=?", (gamertag,))
        if self.c.fetchone():
            return True
        else:
            return False

    def get_day_wl_avg(self, table, user, days=7):
        """ calculates w/l averages """
        total = 0
        sql = str(
            "SELECT COUNT(gamertag_winner) FROM " + str(table) +
            " WHERE gamertag_winner = '" + str(user) + "'" +
            " OR gamertag_loser = '" + str(user) + "'" +
            " AND update_at >= date('now', '-" + str(days) + " days')" +
            " AND update_at <=  date('now','+1 day')" +
            " ORDER BY update_at ASC")
        for row in self.c.execute(sql):
            total = row[0]

        wins = 0
        sql = str(
            "SELECT COUNT(gamertag_winner) FROM " + str(table) +
            " WHERE gamertag_winner = '" + str(user) + "'" +
            " AND update_at >= date('now', '-" + str(days) + " days')" +
            " AND update_at <=  date('now','+1 day')" +
            " AND tie == 0" +
            " ORDER BY update_at ASC")
        for row in self.c.execute(sql):
            wins = row[0]

        try:
            value = round(float(wins) / total, 3)
            return value
        except ZeroDivisionError:
            return 0.0

    def get_day_avg(self, table, user, days=7):
        """ calculates avreage based on number of days """
        sql_string = str(
            "SELECT * FROM " + str(table) +
            " WHERE gamertag = '" + str(user) + "'" +
            " AND update_at >= date('now', '-" + str(days) + " days') " +
            " AND update_at <=  date('now','+1 day') " +
            " ORDER BY update_at ASC")

        recent = []
        average_increase = []
        for row in self.c.execute(sql_string):
            recent.append(row)
            if len(recent) > 1:
                average_increase.append(
                    recent[len(recent) - 1][3] - recent[len(recent) - 2][3])
            else:
                continue

        if len(recent) > 0:
            y, m, d = recent[0][1].split("T")[0].split(" ")[0].split("-")
            min_date = datetime.datetime(int(y), int(m), int(d))
            y, m, d = recent[(len(recent) - 1)][1].split("T")[0].split(" ")[0].split("-")
            max_date = datetime.datetime(int(y), int(m), int(d))
            day_diff = (max_date - min_date).days + 1
            return float(sum(average_increase)) / day_diff
        return 0.0

    @update_decorator
    def update_friend_board(self, gamertag1, gamertag2):
        id = uuid.uuid4()
        sql = str(
            "INSERT OR REPLACE INTO FRIEND_BOARD" +
            " VALUES( " +
            "'" + str(id) + "'," +
            "'" + str(gamertag1) + "'," +
            "'" + str(gamertag2) + "')")
        return sql

    @update_decorator
    def delete_from_friend_board(self, gamertag1, gamertag2):
        sql = str(
            "DELETE FROM FRIEND_BOARD" +
            " WHERE gamertag1 = '" + str(gamertag1) + "' AND" +
            " gamertag2 = '" + str(gamertag2) + "'")
        return sql

    @get_decorator
    def get_friends(self, gamertag, limit=50):
        sql = str(
            "SELECT gamertag1, gamertag2, gamertag, IFNULL(status, 'Offline') " +
            " FROM FRIEND_BOARD " +
            " LEFT JOIN ACTIVE_BOARD " +
            " ON gamertag2 = gamertag " +
            " WHERE gamertag1 = '" + str(gamertag) + "'" +
            " ORDER BY status DESC, gamertag2 ASC" +
            " LIMIT " + str(limit))
        print(sql)
        return sql

    @get_decorator
    def get_online_friends(self, gamertag, limit=50):
        sql = str(
            "SELECT gamertag1, gamertag2, gamertag, IFNULL(status, 'Offline') as status " +
            " FROM FRIEND_BOARD " +
            " LEFT JOIN ACTIVE_BOARD " +
            " ON gamertag2 = gamertag " +
            " WHERE gamertag1 = '" + str(gamertag) + "'" +
            " AND status = 'Online' " +
            " ORDER BY status DESC, gamertag2 ASC" +
            " LIMIT " + str(limit))
        print(sql)
        return sql

    @update_decorator
    def update_active_board(self, gamertag, status):
        id = uuid.uuid4()
        sql = str(
            "INSERT OR REPLACE INTO ACTIVE_BOARD" +
            " VALUES( " +
            "'" + str(id) + "'," +
            "'" + str(gamertag) + "'," +
            "'" + str(status) + "')")
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
    d.update_medal("DepotAgent", "test_account", 10, datetime.datetime.now().isoformat())
    d.update_medal("DepotAgent", "test_account", 15, datetime.datetime.now().isoformat())
    d.update_medal("DepotAgent", "test_account", 25, datetime.datetime.now().isoformat())
    print()
    # d.list_medal("DepotAgent")
    print()
    for x in d.get_recent("DepotAgent", "test_account"):
        print(x)
