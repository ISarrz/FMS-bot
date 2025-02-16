import sqlite3

from modules.database_api import DbGroup
from modules.files_api.paths import database_path
from modules.database_api.dataclasses import Event, Group, DbEvent, DbUser


def update_user_by_id(user_id, telegram_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
                       SELECT * FROM users WHERE id = {user_id}
                       """)


def update_class_user_by_id(user: DbUser):
    update_user_by_id(user.id, user.telegram_id)
