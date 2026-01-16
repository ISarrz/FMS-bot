from modules.data_updater.tools import NodeGroup, EventsGroup, CategoryGroup


def get_timetable_text(root: NodeGroup, date: str):
    result = f"{date}\n"

    if isinstance(root, CategoryGroup):
        result += f"{root.title}\n"
        for child in root.children:
            result += f"{get_timetable_text(child, date)}\n"

    elif isinstance(root, EventsGroup):
        result += f"{root.title}\n"
        for event in root.events:
            result += f"{event.start} - {event.end}\n"
            result += f"{event.name}\n"

    return result
