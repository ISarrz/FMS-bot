import sqlite3
import modules.files_api.paths as pth

from modules.database_api.service.dumps import *
from modules.database_api.db_classes import *
from modules.database_api.interaction.fetch import *
from modules.database_api.interaction.insert import *
from modules.database_api.interaction.update import *
from modules.database_api.interaction.delete import *
from modules.database_api.database.database import DB

DB.initialize()
