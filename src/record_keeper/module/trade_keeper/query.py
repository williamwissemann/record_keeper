from uuid import uuid4

from record_keeper import BOT


@BOT.database.update
def update_trade_board(
    server: str,
    pokemon_number: str,
    pokemon_name: str,
    user: str,
    notes: str = "",
    board: str = "TRADE_BOARD",
) -> list:
    return (
        f"INSERT OR REPLACE INTO {board}"
        f" values('{uuid4()}', '{server}', '{user}',"
        f" '{pokemon_name}',{pokemon_number},"
        f" '{notes}')"
    )


@BOT.database.get
def get_trade_board_by_user(
    server,
    user,
    board: str = "TRADE_BOARD",
):
    sql = f"SELECT pokemon, number, notes FROM {board}"
    sql += f" WHERE gamertag = '{user}'"
    if not server == "ViaDirectMessage":
        sql += f" AND ( server_id = '{server}'"
        sql += " OR server_id = 'ViaDirectMessage')"
    sql += " ORDER BY number ASC"
    return sql


@BOT.database.get
def get_raw_trade_string(
    server,
    user,
    board: str = "TRADE_BOARD",
):
    sql = f"SELECT number FROM {board}"
    sql += f" WHERE gamertag = '{user}'"
    if not server == "ViaDirectMessage":
        sql += f" AND ( server_id = '{server}'"
        sql += " OR server_id = 'ViaDirectMessage')"
    sql += " ORDER BY number ASC"
    return sql


@BOT.database.update
def delete_from_trade_board(
    server,
    pokemon_name,
    user,
    board: str = "TRADE_BOARD",
):
    sql = f"DELETE FROM {board} WHERE gamertag = '{user}'"
    if not server == "ViaDirectMessage":
        sql += f" AND ( server_id = '{server}'"
        sql += " OR server_id = 'ViaDirectMessage')"
    sql += f"AND pokemon = '{pokemon_name}'"
    return sql
