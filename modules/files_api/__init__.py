from modules.files_api.paths import *
from modules.files_api.config import *

os.makedirs(data_path, exist_ok=True)
os.makedirs(database_dumps_path, exist_ok=True)
os.makedirs(downloads_path, exist_ok=True)
os.makedirs(parsed_files_path, exist_ok=True)

print('Files initialized')
