import sqlite3

from modules.database_api import DbGroup
from modules.files_api.paths import database_path
from modules.database_api.db_classes import Event, Group, DbEvent, DbUser


def update_user_by_id(user_id, telegram_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        UPDATE users set telegram_id = {telegram_id} WHERE user_id = {user_id}
        """)


def update_class_user_by_id(user: DbUser):
    update_user_by_id(user.id, user.telegram_id)


def update_group_by_id(group_id: int, name: str, about: str):
    with sqlite3.connect(database_path) as conn:
        cur = conn.cursor()
        cur.execute(f"""
        UPDATE groups set name = '{name}', about = '{about}' WHERE id = {group_id}
        """)


def update_event_by_id(event_id: int, name: str, about: str, date: str, start: str, end: str, owner: str, place: str):
    with sqlite3.connect(database_path) as conn:
        cur = conn.cursor()
        cur.execute(f"""
        UPDATE events set name = '{name}', about = '{about}',
        date = '{date}', start = '{start}', end = '{end}', owner = '{owner}', place = '{place}'
        WHERE id = {event_id}
        """)


def update_notifications_by_id(user_id: int, value:int):
    with sqlite3.connect(database_path) as conn:
        cur = conn.cursor()
        cur.execute(f"""
        UPDATE main.users_notifications set value = {value} WHERE user_id = {user_id}
        """)