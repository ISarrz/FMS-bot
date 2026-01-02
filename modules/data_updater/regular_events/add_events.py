from modules.database.event.event import Event
from modules.database.group.group import Group
from modules.time.dates import get_current_string_dates

clubs = Group(name="Клубы")
courses = Group(name="Спецкурсы")
for str_date in get_current_string_dates():
    pass

# Event.insert()
