from record_keeper import BOT


@BOT.database.update
def create_table_if_not_exist(name: str, sql: str):
    return f"CREATE TABLE IF NOT EXISTS {name} {sql}"


@BOT.database.update
def drop_tables(name: str):
    return f"DROP TABLE {name}"


@BOT.database.get
def get_all_tables() -> str:
    """Generates a list of all the tables in the database.

    Returns:
        str:
    """
    return "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
