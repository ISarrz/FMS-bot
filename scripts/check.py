from modules.database.event.event import Event

ct = 0
for event in Event.all():
    ct += 1

print(ct)