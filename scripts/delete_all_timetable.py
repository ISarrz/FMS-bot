from modules.database.timetable.timetable import Timetable

for timetable in Timetable.all():
    timetable.delete()
