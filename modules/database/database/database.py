import sqlite3

from modules.config.paths import database_path, database_dump_path
import re
import os


class DB:
    users_table_name = "users"
    users_groups_table_name = "users_groups"
    users_notifications_table_name = "users_notifications"
    users_settings_table_name = "users_settings"

    groups_table_name = "groups"
    groups_relations_table_name = "groups_relations"

    events_table_name = "events"

    timetable_table_name = "timetable"

    logs_table_name = "logs"

    @staticmethod
    def save_backup():
        # Убедимся, что исходная база существует
        if not os.path.exists(database_path):
            raise FileNotFoundError(f"Source database not found")

        with sqlite3.connect(database_path) as src_conn:
            with sqlite3.connect(database_dump_path) as dest_conn:
                src_conn.backup(dest_conn, pages=0, progress=None)

    @staticmethod
    def load_backup():
        if not os.path.exists(database_dump_path):
            raise FileNotFoundError(f"Source dump database not found")

        if os.path.exists(database_path):
            os.remove(database_path)

        with sqlite3.connect(database_dump_path) as src_conn:
            with sqlite3.connect(database_path) as dest_conn:
                src_conn.backup(dest_conn, pages=0, progress=None)

    @staticmethod
    def fetch_one(table_name: str, **kwargs):
        where_request = DB.create_where_request(**kwargs)

        with sqlite3.connect(database_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(f"""
                SELECT * FROM {table_name} {where_request}
                """, tuple(kwargs.values()))

            response = cur.fetchone()

        return response

    @staticmethod
    def fetch_many(table_name: str, **kwargs):
        # не доделано, в значения должно подставляться list[tuple]

        where_request = DB.create_where_request(**kwargs)

        with sqlite3.connect(database_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(f"""
            SELECT * FROM {table_name} {where_request}
            """, tuple(kwargs.values()))

            response = cur.fetchall()

        return response

    @staticmethod
    def delete_one(table_name: str, **kwargs):
        where_request = DB.create_where_request(**kwargs)

        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()
            cur.execute(f"""
            DELETE FROM {table_name} {where_request}
            """, tuple(kwargs.values()))

    @staticmethod
    def delete_many(table_name: str, **kwargs):
        # не доделано, в значения должно подставляться list[tuple]

        where_request = DB.create_where_request(**kwargs)

        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()
            cur.executemany(f"""
            DELETE FROM {table_name} {where_request}
            """, tuple(kwargs.values()))

    @staticmethod
    def update_one(table_name: str, row_info: dict, new_values: dict):
        where_request = DB.create_where_request(**row_info)
        set_request = DB.create_set_request(**new_values)
        with sqlite3.connect(database_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(f"""
            UPDATE {table_name} {set_request} {where_request}
            """, tuple(new_values.values()) + tuple(row_info.values()))

    @staticmethod
    def update_many(table_name: str, row_info: dict, new_values: dict):
        # не доделано, в значения должно подставляться list[tuple]

        where_request = DB.create_where_request(**row_info)
        set_request = DB.create_set_request(**new_values)
        with sqlite3.connect(database_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.executemany(f"""
            UPDATE {table_name} {set_request} {where_request}
            """, tuple(new_values.values()) + tuple(row_info.values()))

    @staticmethod
    def find_pattern(text, patterns):
        for pattern in patterns:
            if re.fullmatch(pattern[1], text, re.IGNORECASE):
                return pattern[0]

        return None

    @staticmethod
    def insert_one(table_name: str, **kwargs):
        insert_request = DB.create_insert_request(**kwargs)
        new_id = None
        with sqlite3.connect(database_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(f"""
            INSERT INTO {table_name} {insert_request}
            """, tuple(kwargs.values()))

            new_id= cur.lastrowid

        return new_id

    @staticmethod
    def create_where_request(**kwargs):
        return "WHERE " + " AND ".join(f"{arg} = ?" for arg in kwargs.keys()) if kwargs else ""

    @staticmethod
    def create_set_request(**kwargs):
        return "SET " + ", ".join(f"{arg} = ?" for arg in kwargs.keys()) if kwargs else ""

    @staticmethod
    def create_insert_request(**kwargs):
        if not kwargs:
            return ""

        request = "(" + ", ".join(f"{arg}" for arg in kwargs.keys()) + ") "
        request += "VALUES (" + ", ".join(["?" for _ in range(len(kwargs))]) + ")"

        return request

    @staticmethod
    def initialize():
        DB._create_users_table()
        DB._create_users_groups_table()
        DB._create_events_table()
        DB._create_groups_table()
        DB._create_groups_relations_table()
        DB._create_timetable_table()
        DB._create_logs_table()
        DB._create_users_notifications_table()
        DB._create_users_settings_table()
        print("Database initialized.")

    @staticmethod
    def _create_users_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS users
                        (
                            id          INTEGER PRIMARY KEY AUTOINCREMENT,
                            telegram_id INTEGER
                        )""")

    @staticmethod
    def _create_users_groups_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS users_groups
                        (
                            id       INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id  INTEGER REFERENCES users,
                            group_id INTEGER REFERENCES groups
                        )""")

    @staticmethod
    def _create_events_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS events
                        (
                            id       INTEGER PRIMARY KEY AUTOINCREMENT,
                            name     TEXT,
                            group_id INTEGER REFERENCES groups,
                            date     TEXT,
                            start    TEXT,
                            end      TEXT,
                            owner    TEXT,
                            place    TEXT
                        )""")

    @staticmethod
    def _create_groups_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS groups
                        (
                            id   INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT
                        )""")

    @staticmethod
    def _create_groups_relations_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS groups_relations
                        (
                            id        INTEGER PRIMARY KEY AUTOINCREMENT,
                            parent_id INTEGER REFERENCES groups,
                            child_id  INTEGER REFERENCES groups
                        )""")

    @staticmethod
    def _create_timetable_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS timetable
                        (
                            id      INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER REFERENCES users,
                            date    TEXT,
                            image   BLOB
                        )""")

    @staticmethod
    def _create_logs_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS logs
                        (
                            id    INTEGER PRIMARY KEY AUTOINCREMENT,
                            value TEXT
                        )""")

    @staticmethod
    def _create_users_settings_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS users_settings
                        (
                            id            INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id       parent_id INTEGER REFERENCES users,
                            notifications INT
                        )""")

    @staticmethod
    def _create_users_notifications_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS users_notifications
                        (
                            id      INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id parent_id INTEGER REFERENCES users,
                            value   TEXT
                        )""")


if __name__ == "__main__":
    DB.save_backup()
    DB.load_backup()
    pass
