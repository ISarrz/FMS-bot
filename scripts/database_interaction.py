from scripts.data_updater import make_database_backup
from modules.database.database.database import DB

if __name__ == "__main__":
    print("Save database - 0\n Load database - 1")

    if input() == "0":
        make_database_backup()

    elif input() == "1":
        DB.load_last_backup()

    print("Done")
