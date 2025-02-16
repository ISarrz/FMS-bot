import sqlite3

from modules.database_api import DbGroup, DbEvent, DbUser
from modules.files_api.paths import database_path


def fetch_by_id(table_name, row_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
                       SELECT * FROM {table_name} WHERE id = {row_id}
                       """)

        response = cur.fetchone()

    return response


def fetch_event_by_id(event_id: int):
    return fetch_by_id('events', event_id)


def fetch_class_event_by_id(event_id: int):
    response = fetch_event_by_id(event_id)
    event = DbEvent(id=response['id'], name=response['name'], about=response['about'], start=response['start'],
                    end=response['end'], owner=response['owner'], place=response['place'])

    return event


def fetch_events_by_date(date: str):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
                       SELECT * FROM events WHERE date = '{date}'
                       """)

        response = cur.fetchall()

    return response


def fetch_all_events():
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
                           SELECT * FROM events 
                           """)

        response = cur.fetchall()

    return response


def fetch_all_groups():
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
                           SELECT * FROM groups 
                           """)

        response = cur.fetchall()

    return response
def fetch_group_by_id(group_id: int):
    return fetch_by_id('groups', group_id)


def fetch_group_by_name(name: str):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
                       SELECT * FROM groups WHERE name = '{name}'
                       """)

        response = cur.fetchone()

    return response


def fetch_class_group_by_name(name: str):
    response = fetch_group_by_name(name)
    if not response:
        return None

    return DbGroup(id=response['id'], name=response['name'], about=response['about'])


def fetch_class_group_by_id(group_id: int):
    response = fetch_group_by_id(group_id)
    group = DbGroup(id=response['id'], name=response['name'], about=response['about'])

    return group


def fetch_user_by_id(user_id: int):
    return fetch_by_id('users', user_id)


def fetch_class_user_by_id(user_id: int):
    response = fetch_user_by_id(user_id)
    user = DbUser(id=response['id'], telegram_id=response['telegram_id'])

    return user


if __name__ == '__main__':
    res = fetch_class_group_by_name("Группа А")
    pass
