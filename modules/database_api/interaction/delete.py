import sqlite3

from modules.database_api import DbGroup, DbEvent, DbUser
from modules.files_api.paths import database_path


def delete_by_id(table_name, row_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
                       DELETE FROM {table_name} WHERE id = {row_id}
                       """)


def delete_event_by_id(event_id: int):
    delete_by_id('events', event_id)


def delete_class_event_by_id(event: DbEvent):
    delete_event_by_id(event.id)
