import sqlite3


class Sqlite3Wrapper:
    """A small wrapper for sqlite3 to replace some repetitive.

    Args:
        database_path (str, optional): Path to a sqlite3 file.
        Defaults to "test.db".
    """

    def __init__(self, database_path: str = "test.db"):
        """Creates a cursor to handle database interactions."""
        self.conn = sqlite3.connect(database_path)
        self.cursor = self.conn.cursor()

    def get(self, func) -> list:
        """Wrappers for querying data (i.e SELECT)

        Args:
            func: takes function which returns a sql query as a string

        Returns:
            list: returns an array with the results from query.
        """

        def wrapper(*args, **kwargs):
            sql_string = func(*args, **kwargs)
            recent = []
            for row in self.cursor.execute(sql_string):
                recent.append(row)
            return recent

        return wrapper

    def update(self, func) -> None:
        """Wrapper for a modifying sql query (i.e INSERT/REPLACE/UPDATE/DELETE).

        Args:
             func: takes function which returns a sql query as a string.

        Returns:
            None
        """

        def wrapper(*args, **kwargs):
            sql_string = func(*args, **kwargs)
            self.cursor.execute(sql_string)
            self.conn.commit()

        return wrapper
