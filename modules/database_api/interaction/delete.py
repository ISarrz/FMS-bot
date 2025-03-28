import sqlite3

from modules.database_api import DbGroup, DbEvent, DbUser
from modules.database_api.interaction.fetch import *
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


def delete_group_events_by_id(group_id: int):
    for event in fetch_group_events_by_id(group_id):
        delete_by_id('events', event['id'])


def delete_group_and_relations_by_id(group_id: int):
    while fetch_child_by_id(group_id):
        child = fetch_child_by_id(group_id)
        delete_group_and_relations_by_id(child['id'])

    parent = fetch_parent_by_id(group_id)
    delete_groups_relation_by_groups_id(parent['id'], group_id)
    delete_group_events_by_id(group_id)
    delete_by_id('groups', group_id)


def delete_user_group(user_id: int, group_id):
    with sqlite3.connect(database_path) as conn:
        cur = conn.cursor()
        cur.execute(f"""
        DELETE FROM users_groups WHERE user_id = {user_id} AND group_id = {group_id}
        """)


def delete_users_updates_by_id(users_updates_id: int):
    with sqlite3.connect(database_path) as conn:
        cur = conn.cursor()
        cur.execute(f"""
        DELETE FROM users_updates WHERE id = {users_updates_id} 
        """)


def delete_user_group_and_relations(user_id: int, group_id: int):
    child = fetch_user_groups_by_parent_group_id(user_id, group_id)

    for group in child:
        delete_user_group_and_relations(user_id, group['id'])

    delete_user_group(user_id, group_id)
    delete_user_updates_by_user_id_and_group_id(user_id, group_id)


def delete_group_event_by_group_and_event_id(group_id: int, event_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
                       DELETE FROM groups_events WHERE group_id = {group_id} AND event_id = {event_id}
                       """)


def delete_group_event_by_event_id(event_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        DELETE FROM groups_events WHERE event_id = {event_id}
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


def delete_image_by_date_and_group_id(date: str, group_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        DELETE FROM images WHERE date={date} AND group_id = {group_id}
        """)


def delete_logs_by_id(logs_id: int):
    delete_by_id('logs', logs_id)


def delete_user_updates_by_date_and_group_id(date: str, group_id: int):
    groups = fetch_groups_sequence(group_id)
    for group in groups:
        with sqlite3.connect(database_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(f"""
            DELETE FROM users_updates WHERE date={date} AND group_id = {group['id']}
            """)

def delete_user_updates_by_user_id_and_group_id(user_id:int, group_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        DELETE FROM users_updates WHERE user_id={user_id} AND group_id = {group_id}
        """)


