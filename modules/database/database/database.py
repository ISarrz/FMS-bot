import sqlite3
import xml.etree.ElementTree as ET
from modules.config.paths import database_path
from modules.config.config import get_config_field
import re
from datetime import datetime
import subprocess
import boto3
from botocore.exceptions import NoCredentialsError


class DB:
    users_table_name = "users"
    users_groups_table_name = "users_groups"
    users_notifications_table_name = "users_notifications"
    users_settings_table_name = "users_settings"

    groups_table_name = "groups"
    groups_relations_table_name = "groups_relations"

    events_table_name = "events"
    regular_events_table_name = "regular_events"
    events_from_regular_events_table_name = "events_from_regular_events"
    free_dates_for_regular_events_table_name = "free_dates_for_regular_events"

    timetable_table_name = "timetable"

    logs_table_name = "logs"

    @staticmethod
    def make_backup():
        cur_date = datetime.now().strftime("%d-%m-%Y")
        session = boto3.session.Session()
        s3 = session.client(
            service_name='s3',
            endpoint_url='https://storage.yandexcloud.net',
            aws_access_key_id=get_config_field('yandex_key'),
            aws_secret_access_key=get_config_field('yandex_secret_key'),
            region_name='ru-central1'
        )

        try:
            s3.upload_file(database_path, get_config_field("yandex_bucket_address"), f"{cur_date}.db")
            return True

        except FileNotFoundError:
            return False

        except NoCredentialsError:
            return False

    @staticmethod
    def load_backup(backup_name: str):
        s3 = boto3.client(
            service_name='s3',
            endpoint_url='https://storage.yandexcloud.net',
            aws_access_key_id=get_config_field('yandex_key'),
            aws_secret_access_key=get_config_field('yandex_secret_key'),
            region_name='ru-central1'
        )

        try:
            s3.download_file(
               get_config_field("yandex_bucket_address") ,
                backup_name,
                database_path
            )
            return True

        except Exception as e:
            return False

    @staticmethod
    def get_backups_names():
        s3 = boto3.client(
            service_name='s3',
            endpoint_url='https://storage.yandexcloud.net',
            aws_access_key_id=get_config_field('yandex_key'),
            aws_secret_access_key=get_config_field('yandex_secret_key'),
            region_name='ru-central1'
        )

        bucket_name = get_config_field("yandex_bucket_address")

        try:
            response = s3.list_objects_v2(Bucket=bucket_name)

            if 'Contents' in response:
                files = [obj['Key'] for obj in response['Contents']]
                return files

            return []
        except Exception:
            return []

    @staticmethod
    def load_last_backup():
        backups_names = DB.get_backups_names()
        backups_names.sort(key=lambda s: datetime.strptime(s.split(".")[0], "%d-%m-%Y"))
        print(backups_names[-1])
        return DB.load_backup(backups_names[-1])

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

            new_id = cur.lastrowid

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
        try:
            DB._create_users_table()
            DB._create_users_groups_table()
            DB._create_events_table()
            DB._create_regular_events_table()
            DB._create_groups_table()
            DB._create_groups_relations_table()
            DB._create_timetable_table()
            DB._create_logs_table()
            DB._create_users_notifications_table()
            DB._create_users_settings_table()
            DB._create_free_dates_for_regular_events_table()
            DB._create_events_from_regular_events_tabe()

        except Exception:
            print("Database initialization failed")
            return

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
    def _create_events_from_regular_events_tabe():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS events_from_regular_events
                        (
                            id               INTEGER PRIMARY KEY AUTOINCREMENT,
                            event_id         INTEGER REFERENCES events,
                            regular_event_id INTEGER REFERENCES regular_events
                        )""")

    @staticmethod
    def _create_regular_events_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS regular_events
                        (
                            id       INTEGER PRIMARY KEY AUTOINCREMENT,
                            name     TEXT,
                            group_id INTEGER REFERENCES groups,
                            weekday  INTEGER,
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
                            text    TEXT,
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
                            notifications INT,
                            mode          TEXT
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

    @staticmethod
    def _create_free_dates_for_regular_events_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS free_dates_for_regular_events
                        (
                            id               INTEGER PRIMARY KEY AUTOINCREMENT,
                            regular_event_id parent_id INTEGER REFERENCES regular_events,
                            date             TEXT
                        )""")


if __name__ == "__main__":
    pass
