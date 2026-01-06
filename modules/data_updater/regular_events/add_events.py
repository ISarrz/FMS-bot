from modules.database.event.regular_event import RegularEvent


def generate_events():
    for regular_event in RegularEvent.all():
        regular_event.generate_events()

# Event.insert()
