from uuid import uuid4

from record_keeper import BOT


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
