from modules.database.database.database import DB
from modules.database.user.user import User, UserSettings, UserNotification
from modules.database.event.event import Event
from modules.database.group.group import Group
from modules.database.log.log import Log
from modules.database.timetable.timetable import Timetable, TimetableNotFoundError, IncorrectTimetableArgumentsError

DB.initialize()
