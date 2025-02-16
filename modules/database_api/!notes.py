import sqlite3

try:
    conn = sqlite3.connect("../database.db")
    cur = conn.cursor()
    file_path = f"../database_dumps/{dump_name}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w") as sql_file:
        for line in conn.iterdump():
            sql_file.write(line)

except sqlite3.Error as e:
    if conn:
        conn.rollback()
finally:
    if conn:
        conn.close()




def create_database():



    with sqlite3.connect("database.db") as conn:
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


def delete_database():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

        cur.execute("DROP TABLE IF EXISTS users")
        cur.execute("DROP TABLE IF EXISTS events")
        cur.execute("DROP TABLE IF EXISTS groups")
        cur.execute("DROP TABLE IF EXISTS groups_relations")
        cur.execute("DROP TABLE IF EXISTS groups_events")
        cur.execute("DROP TABLE IF EXISTS users_groups")


# SELECT 1, 2, 3 FROM table WHERE score < 100
# SELECT 1, 2, 3 FROM table WHERE score < 100 and age > 10
# SELECT 1, 2, 3 FROM table WHERE score IN(10,20) and age > 10
# ORDER BY old ASC возрастание
# ORDER BY old DESC убывание
# LIMIT 2
# res cur.fetchall
# SELECT 1, 2, 3 FROM table WHERE score BETWEEN 10 AND 100

def insert_event(name, about, start, end, owner, place):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

        cur.execute(f"""
        INSERT INTO events (name, about, start, end, owner, place)
        VALUES ({name}, {about}, {start}, {end}, {owner}, {place})
        """)

        event_id = cur.lastrowid

    return event_id


def insert_group(name, about, start, end, owner, place):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute(f"""
        INSERT INTO groups (name, about) VALUES ({name}, {about})
        """)

        group_id = cur.lastrowid

    return group_id


def insert_user(telegram_id):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute(f"""
        INSERT INTO users (telegram_id) VALUES ({telegram_id})
        """)

        user_id = cur.lastrowid

    return user_id


def fetch_user(telegram_id, type=tuple):
    with sqlite3.connect('database.db') as conn:
        if type == dict:
            conn.row_factory = sqlite3.Row

        cur = conn.cursor()
        cur.execute(f"""
        SELECT * FROM users WHERE telegram_id = {telegram_id} 
        """)

    return cur.fetchone()


def make_dump():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        for i in conn.iterdump():
            pass


if __name__ == '__main__':
    # delete_database()
    create_database()
