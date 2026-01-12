from scripts.data_updater import make_database_backup
from modules.database.database.database import DB

if __name__ == "__main__":
    print("Save database - 0\n Load database - 1")

    inp = input()
    if inp == "0":
        make_database_backup()

    elif inp == "1":
        DB.load_last_backup()

    print("Done")
