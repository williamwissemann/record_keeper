from record_keeper import BOT


@BOT.database.update
def create_table_if_not_exist(name: str, sql: str):
    """Creates tables if the don't exist in the database.

    Args:
        name (str): The name of the table.
        sql (str): The SQL string to define the tables columns.

    Returns:
        None
    """
    return f"CREATE TABLE IF NOT EXISTS {name} {sql}"


@BOT.database.update
def drop_tables(name: str):
    """A drop table sql query.

    Args:
        name (str): Name of the table

    Returns:
        None
    """
    return f"DROP TABLE {name}"


@BOT.database.get
def get_all_tables() -> str:
    """Generates a list of all the tables in the database.

    Returns:
        list: [(table_name_1,), (table_name_2,), ...]
    """
    return "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
