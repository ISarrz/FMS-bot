import sqlite3

from modules.database_api.user import User
from modules.database_api.group import Group
from modules.database_api.event import Event
from modules.files_api.paths import database_path


class DB:
    user = User()
    group = Group()
    event = Event()

    @staticmethod
    def fetch_all(table_name: str, **kwargs):
        request = "WHERE" + " AND ".join(f"{arg} = ?" for arg in kwargs.keys()) if kwargs else ""

        with sqlite3.connect(database_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(f"""
            SELECT * FROM {table_name} {request}
            """, tuple(kwargs.values()))

            response = cur.fetchall()

        return response

    @staticmethod
    def fetch_one(table_name: str, **kwargs):
        request = "WHERE" + " AND ".join(f"{arg} = ?" for arg in kwargs.keys()) if kwargs else ""

        with sqlite3.connect(database_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(f"""
            SELECT * FROM {table_name} {request}
            """, tuple(kwargs.values()))

            response = cur.fetchone()

        return response

    @staticmethod
    def initialize():
        DB._create_users_table()
        DB._create_users_groups_table()
        DB._create_events_table()
        DB._create_groups_table()
        DB._create_groups_events_table()
        DB._create_groups_relations_table()
        DB._create_images_table()
        DB._create_logs_table()
        DB._create_users_notifications_table()
        DB._create_users_updates_table()

    @staticmethod
    def _create_users_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER
            )""")

    @staticmethod
    def _create_users_groups_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS users_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users,
            group_id INTEGER REFERENCES groups
            )""")

    @staticmethod
    def _create_events_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            about TEXT,
            date TEXT,
            start TEXT,
            end TEXT,
            owner TEXT,
            place TEXT
            )""")

    @staticmethod
    def _create_groups_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            about TEXT
            )""")

    @staticmethod
    def _create_groups_relations_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS groups_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER REFERENCES groups,
            child_id INTEGER REFERENCES groups
            )""")

    @staticmethod
    def _create_groups_events_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS groups_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER REFERENCES groups,
            event_id INTEGER REFERENCES events
            )""")

    @staticmethod
    def _create_images_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image BLOB,
            date TEXT,
            group_id INTEGER REFERENCES groups
            )""")

    @staticmethod
    def _create_logs_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            value TEXT
            )""")

    @staticmethod
    def _create_users_notifications_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS users_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id parent_id INTEGER REFERENCES users,
            value INTEGER
            )""")

    @staticmethod
    def _create_users_updates_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS users_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            group_id INTEGER REFERENCES groups,
            user_id INTEGER REFERENCES users
            )""")
