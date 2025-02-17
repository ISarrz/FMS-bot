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


def delete_group_by_id(group_id: int):
    delete_by_id('groups', group_id)


def delete_group_event_by_group_and_event_id(group_id: int, event_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
                       DELETE FROM groups_events WHERE group_id = {group_id} AND event_id = {event_id}
                       """)


def delete_groups_relation_by_groups_id(parent_id: int, child_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
                       DELETE FROM groups_relations WHERE parent_id = {parent_id} AND child_id = {child_id}
                       """)


def delete_image_by_id(image_id: int):
    delete_by_id('images', image_id)
