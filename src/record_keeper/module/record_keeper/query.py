from uuid import uuid4

from record_keeper import BOT


@BOT.database.update
def update_medal(
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
    server: str,
    table: str,
    user: str,
    limit: int = 25,
    uuid: bool = False,
) -> list:
    sql = f"SELECT update_at, value, note"
    sql += f" FROM {str(table)} WHERE gamertag = '{str(user)}'"
    if not server == "ViaDirectMessage":
        sql += f" AND ( server_id = '{str(server)}'"
        sql += " OR server_id = 'ViaDirectMessage')"
    if uuid:
        sql += " AND update_at >= datetime('now', '-1 day') "
        sql += " AND update_at <= datetime('now', '+1 day') "
    sql += " ORDER BY update_at DESC"
    sql += f" LIMIT {limit}"
    return sql


@BOT.database.get
def get_avg_per_day(server: str, table: str, user: str, days: int) -> list:
    return (
        f"SELECT AVG(VALUE) FROM {table}"
        f" WHERE gamertag = '{user}'"
        f" AND update_at > datetime('now','-{days} days')"
    )


@BOT.database.get
def get_leaderboard(
    server: str,
    table: str,
    limit: int = 25,
):
    if table.lower() in ["stardust"]:
        sql = f"SELECT update_at, gamertag, value, note FROM {table}"
    else:
        sql = f"SELECT update_at, gamertag, MAX(value), note FROM {table}"
    if not server == "ViaDirectMessage":
        sql += f" WHERE (server_id = '{server}'"
        sql += " OR server_id = 'ViaDirectMessage')"
    sql += " GROUP BY gamertag"
    sql += " ORDER BY value DESC, update_at ASC"
    sql += " LIMIT 25"
    return sql
