import sqlite3
from modules.files_api.paths import database_dumps_path, database_path
import os


def save_dump(dump_name="database_dump.db"):
    with sqlite3.connect(database_path) as conn:
        cur = conn.cursor()
        file_path = os.path.join(database_dumps_path, dump_name)

        with open(file_path, "w") as sql_file:
            for line in conn.iterdump():
                sql_file.write(line)

def create_backup():
    src = sqlite3.connect(database_path)
    dump_name = "database_dump.db"
    file_path = os.path.join(database_dumps_path, dump_name)
    dst = sqlite3.connect(file_path)
    with dst:
        src.backup(dst)
    dst.close()
    src.close()

def load_dump(dump_name="database_dump.db"):
    with sqlite3.connect(database_path) as conn:
        cur = conn.cursor()
        file_path = os.path.join(database_dumps_path, dump_name)

        with open(file_path) as file:
            sql = file.read()
            cur.executescript(sql)


if __name__ == "__main__":
    # save_dump()
    # create_backup()
    load_dump()
