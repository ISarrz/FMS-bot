from modules.files_api.paths import *

os.makedirs(data_path, exist_ok=True)
os.makedirs(database_dumps_path, exist_ok=True)

print('Files initialized')
