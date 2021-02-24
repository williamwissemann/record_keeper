import os

import pytest

from record_keeper.utilities.sqlite3_wrapper import Sqlite3Wrapper

database_name = "Sqlite3Wrapper_test.db"
database = Sqlite3Wrapper(database_path="Sqlite3Wrapper_test.db")


@database.update
def create_table():
    return "CREATE TABLE IF NOT EXISTS TEST_TABLE (uuid text, field text, info text)"


@database.update
def insert_data(uuid, field, info):
    return f"INSERT INTO TEST_TABLE VALUES('{uuid}', '{field}', '{info}')"


@database.get
def get_data(uuid, field, info):
    return f"SELECT * FROM TEST_TABLE"


def test_Sqlite3Wrapper_test():
    create_table()
    insert_data("1", "2", "3")
    insert_data("2", "5", "8")
    insert_data("3", "6", "9")

    try:
        results = get_data("4", "7", "10")
        expected = [
            ("1", "2", "3"),
            ("2", "5", "8"),
            ("3", "6", "9"),
        ]
        assert results == expected
    finally:
        os.remove("Sqlite3Wrapper_test.db")
