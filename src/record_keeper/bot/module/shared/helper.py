from record_keeper import BOT


@BOT.database.update
def create_table_if_not_exist(name: str, sql: str) -> None:
    return f"CREATE TABLE IF NOT EXISTS {name} {sql}"


@BOT.database.update
def drop_tables(name: str) -> None:
    return f"DROP TABLE {name}"


@BOT.database.get
def get_all_tables() -> list:
    return "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
