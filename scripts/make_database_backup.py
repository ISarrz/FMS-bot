from scripts.data_updater import make_database_backup
from modules.database.database.database import DB
if __name__ == "__main__":
    print(0)
    DB.make_backup()
    print(1)
