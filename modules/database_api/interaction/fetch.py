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
                    end=response['end'], owner=response['owner'], place=response['place'], date=response['date'])

    return event


def fetch_event_groups_by_id(event_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        SELECT groups.id, groups.name, groups.about
        FROM groups_events 
        JOIN groups ON groups.id = groups_events.group_id 
        WHERE groups_events.event_id = {event_id}
        """)

        response = cur.fetchall()

    return response


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


def fetch_group_by_parent_id_and_name(parent_id: int, name: str):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
                SELECT groups.id, groups.name, groups.about FROM groups_relations JOIN groups ON groups_relations.child_id = groups.id 
                WHERE groups_relations.parent_id = {parent_id} AND groups.name = '{name}'
                """)
        response = cur.fetchone()

    return DbGroup(id=response['id'], name=response['name'], about=response['about'])


def fetch_parent_by_id(child_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        SELECT groups.id, groups.name, groups.about FROM groups_relations JOIN groups ON groups_relations.parent_id = groups.id 
        WHERE groups_relations.child_id = {child_id}
        """)

        response = cur.fetchone()

    return response


def fetch_class_parent_by_id(child_id: int):
    fetch_parent = fetch_parent_by_id(child_id)
    if fetch_parent:
        return DbGroup(id=fetch_parent['id'], name=fetch_parent['name'], about=fetch_parent['about'])

    return None


def fetch_child_by_id(parent_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        SELECT groups.id, groups.name, groups.about FROM groups_relations JOIN groups ON groups_relations.child_id = groups.id 
        WHERE groups_relations.parent_id = {parent_id}
        """)

        response = cur.fetchone()

    return response


def fetch_all_class_child_by_id(parent_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
                SELECT groups.id, groups.name, groups.about FROM groups_relations JOIN groups ON groups_relations.child_id = groups.id 
                WHERE groups_relations.parent_id = {parent_id}
                """)
        response = cur.fetchall()

    result = []
    for group in response:
        db_group = DbGroup(id=group['id'], name=group['name'], about=group['about'])
        result.append(db_group)

    return result


def fetch_class_group_by_name(name: str):
    response = fetch_group_by_name(name)
    if not response:
        return None

    return DbGroup(id=response['id'], name=response['name'], about=response['about'])


def fetch_group_by_name_and_parent_id(name: str, parent_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        SELECT groups.id, groups.name, groups.about FROM groups 
        JOIN groups_relations ON groups_relations.child_id = groups.id 
        WHERE groups_relations.parent_id = {parent_id} AND groups.name = '{name}'
    """)
        response = cur.fetchone()

    return response


def fetch_class_group_by_id(group_id: int):
    response = fetch_group_by_id(group_id)
    group = DbGroup(id=response['id'], name=response['name'], about=response['about'])

    return group


def fetch_user_by_id(user_id: int):
    return fetch_by_id('users', user_id)


def fetch_user_by_telegram_id(telegram_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
           SELECT * FROM users WHERE telegram_id = {telegram_id}
           """)

        response = cur.fetchone()

    return response


def fetch_user_groups_by_id(user_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        SELECT * FROM groups JOIN users_groups ON groups.id = users_groups.group_id 
        WHERE users_groups.user_id = {user_id}
    """)
        response = cur.fetchall()

    return response


def fetch_groups_sequence(child_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        response = [fetch_group_by_id(child_id)]
        while True:
            cur.execute(f"""
            SELECT * FROM groups_relations WHERE child_id = {child_id}
            """)

            cur_response = cur.fetchone()
            if cur_response is None:
                break

            child_id = cur_response['parent_id']
            response.append(fetch_group_by_id(child_id))

        return response


def fetch_class_user_by_id(user_id: int):
    response = fetch_user_by_id(user_id)
    user = DbUser(id=response['id'], telegram_id=response['telegram_id'])

    return user


def fetch_user_groups_by_parent_group_id(user_id: int, parent_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        SELECT * FROM groups JOIN users_groups  ON groups.id = users_groups.group_id 
        JOIN groups_relations ON groups.id = groups_relations.child_id 
         
         WHERE groups_relations.parent_id = {parent_id} AND user_id = {user_id}
        """)

        response = cur.fetchall()

    return response


def fetch_class_user_by_telegram_id(telegram_id: int):
    response = fetch_user_by_telegram_id(telegram_id)
    user = DbUser(id=response['id'], telegram_id=response['telegram_id'])

    return user


def fetch_image_by_date_and_group_id(date: str, group_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        SELECT image FROM images WHERE date = '{date}' AND group_id = {group_id}
        """)

        response = cur.fetchone()
        response = response['image'] if response else None

    return response


def fetch_image_id_by_date_and_group_id(date: str, group_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        SELECT id FROM images WHERE date = '{date}' AND group_id = {group_id}
        """)

        response = cur.fetchone()
        response = response['id'] if response else None

    return response


def fetch_image_id_by_group_id(group_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
SELECT id FROM images WHERE group_id = {group_id}
""")


def fetch_all_images():
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
        SELECT * from images 
        """)

        response = cur.fetchall()

    return response


def fetch_all_users():
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        SELECT * from users     
        """)

        response = cur.fetchall()

    return response


def fetch_all_users_updates():
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        SELECT * from users_updates    
        """)

        response = cur.fetchall()

    return response


def fetch_all_class_users():
    users = fetch_all_users()
    response = []
    for user in users:
        response.append(DbUser(id=user['id'], telegram_id=user['telegram_id']))

    return response


def fetch_group_events_by_id(group_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        SELECT * FROM events JOIN groups_events ON groups_events.event_id = events.id
        WHERE groups_events.group_id = {group_id} 
    """)

        response = cur.fetchall()

    return response


def fetch_group_events_by_group_id_and_date(group_id: int, date: str):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        SELECT * FROM events JOIN groups_events ON groups_events.event_id = events.id
        WHERE groups_events.group_id = {group_id} AND events.date = '{date}' 
    """)

        response = cur.fetchall()

    return response


def fetch_user_notifications(user_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        SELECT value FROM users_notifications WHERE user_id = {user_id}
        """)

        response = cur.fetchone()

        return response


def fetch_user_update_groups_by_date(user_id: int, date: str):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        SELECT * FROM groups JOIN users_updates ON users_updates.group_id = groups.id 
        WHERE users_updates.user_id = {user_id} AND users_updates.date = '{date}'
        """)

        response = cur.fetchall()

    return response


def fetch_user_update_dates_by_id(user_id: int):
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        SELECT users_updates.date FROM groups JOIN users_updates ON users_updates.group_id = groups.id 
        WHERE users_updates.user_id = {user_id}
        """)

        response = cur.fetchall()
    response = [date['date'] for date in response]

    return response


def fetch_all_logs():
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"""
        SELECT * FROM logs
        """)

        response = cur.fetchall()

    return response


if __name__ == '__main__':
    res = fetch_class_parent_by_id(2)
    pass
