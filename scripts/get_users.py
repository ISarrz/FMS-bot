from modules.database_api import *

q = fetch_all_users()
for i in q:
    print(i['telegram_id'])