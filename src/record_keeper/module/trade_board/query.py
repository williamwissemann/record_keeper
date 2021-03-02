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