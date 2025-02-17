import sqlite3

from modules.files_api.paths import database_path
from modules.database_api.dataclasses import Event, Group


def insert_event(name: str, about: str, date: str, start: str, end: str, owner: str, place: str) -> int:
    with sqlite3.connect(database_path) as conn:
        cur = conn.cursor()
        cur.execute(f"""
                    INSERT INTO events (name, about, date, start, end, owner, place)
                    VALUES ('{name}', '{about}', '{date}', '{start}', '{end}', '{owner}', '{place}')
                    """)

        event_id = cur.lastrowid

    return event_id


def insert_class_event(event: Event):
    insert_event(name=event.name, about=event.about, date=event.date,
                 start=event.start, end=event.end, owner=event.owner,
                 place=event.place)


def insert_user(telegram_id: int) -> int:
    with sqlite3.connect(database_path) as conn:
        cur = conn.cursor()

        cur.execute(f"""
        INSERT INTO users (telegram_id) VALUES ({telegram_id})
        """)

        user_id = cur.lastrowid

    return user_id


def insert_group(name: str, about: str):
    with sqlite3.connect(database_path) as conn:
        cur = conn.cursor()
        cur.execute(f"""
        INSERT INTO groups (name, about) VALUES ('{name}', '{about}')
        """)

        group_id = cur.lastrowid

    return group_id


def insert_class_group(group: Group):
    insert_group(group.name, group.about)


def insert_groups_relation(parent_id, child_id):
    with sqlite3.connect(database_path) as conn:
        cur = conn.cursor()
        cur.execute(f"""
        INSERT INTO groups_relations (parent_id, child_id) VALUES ({parent_id}, {child_id})
        """)

        relation_id = cur.lastrowid

    return relation_id


def insert_user_group(user_id, group_id):
    with sqlite3.connect(database_path) as conn:
        cur = conn.cursor()
        cur.execute(f"""
        INSERT INTO users_groups (user_id, group_id) VALUES ({user_id}, {group_id})
        """)

        relation_id = cur.lastrowid

    return relation_id


def insert_group_event(group_id, event_id):
    with sqlite3.connect(database_path) as conn:
        cur = conn.cursor()
        cur.execute(f"""
        INSERT INTO groups_events (group_id, event_id) VALUES ({group_id}, {event_id})
        """)

        relation_id = cur.lastrowid

    return relation_id


def insert_image(image, date: str, group_id: int):
    with sqlite3.connect(database_path) as conn:
        cur = conn.cursor()
        cur.execute(f"""
        INSERT INTO images (image, date, group_id) VALUES ({image}, '{date}',{group_id})
        """)

        relation_id = cur.lastrowid

    return relation_id


if __name__ == '__main__':
    pass
