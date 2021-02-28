from uuid import uuid4

from record_keeper import BOT


@BOT.database.update
def update_medal(
    self,
    server: str,
    table: str,
    user_id: str,
    value: float,
    update_at: str,
    notes: str = "",
) -> list:

    value = float(value)
    update_at.replace(" ", "T")

    return (
        f"INSERT INTO {table} "
        f"values('{uuid4}','{server}','{update_at}','{user_id}',{value},"
        f"'{notes}')"
    )


@BOT.database.get
def get_recent(
    self,
    server: str,
    table: str,
    user: str,
    limit: int = 25,
    uuid: bool = False,
) -> list:
    sql = f"SELECT * FROM {str(table)} WHERE gamertag = f'{str(user)}'"
    if not server == "ViaDirectMessage":
        sql += f" AND ( server_id = '{str(server)}' OR server_id = 'ViaDirectMessage')"
    if uuid:
        sql += " AND update_at >= datetime('now', '-1 day') "
        sql += " AND update_at <= datetime('now', '+1 day') "
    sql += " ORDER BY update_at DESC"
    sql += " LIMIT " + str(limit)
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


# XXXX
@BOT.database.get
def has_listener(server: str, channel: str, toggle: str) -> str:
    return (
        "SELECT * FROM listener"
        f" WHERE server_id = '{server}'"
        f" AND toggle = '{toggle}'"
        f" AND active_channel = '{channel}'"
    )


@BOT.database.get
def get_listeners(server: str, channel: str) -> str:
    sql = "SELECT * FROM listener"
    if not server == "ViaDirectMessage":
        sql += f" WHERE server_id = '{server}'"
        sql += f" AND active_channel = '{channel}'"

    return sql


@BOT.database.update
def update_listener(server: str, channel: str, toggle: str) -> str:
    return (
        "INSERT or IGNORE INTO listener"
        f" values('{uuid4()}', '{server}', '{toggle}', '{channel}')"
    )


@BOT.database.update
def remove_listener(server: str, channel: str, toggle: str) -> str:
    return (
        "DELETE FROM listener"
        f" WHERE server_id = {server}"
        f" AND active_channel = '{channel}'"
        f" AND toggle = '{toggle}'"
    )
