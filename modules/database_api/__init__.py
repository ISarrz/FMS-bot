import sqlite3
import modules.files_api.paths as pth

from modules.database_api.service.dumps import *
from modules.database_api.dataclasses import *
from modules.database_api.interaction.fetch import *
from modules.database_api.interaction.insert import *
from modules.database_api.interaction.update import *
from modules.database_api.interaction.delete import *

with sqlite3.connect(pth.database_path) as conn:
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER
        )""")

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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        about TEXT
        )""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS groups_relations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_id INTEGER REFERENCES groups,
        child_id INTEGER REFERENCES groups
        )""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS groups_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER REFERENCES groups,
        event_id INTEGER REFERENCES events
        )""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users,
        group_id INTEGER REFERENCES groups
        )""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image BLOB,
        date TEXT,
        group_id INTEGER REFERENCES groups
        )""")

    print("Database initialized")
