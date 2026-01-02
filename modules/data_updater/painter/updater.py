import datetime

from modules.database.user.user import User
from modules.database.event.event import Event
from modules.time.dates import get_current_string_dates
from PIL import ImageFont, ImageDraw, Image
from modules.data_updater.painter.table import Table
from modules.data_updater.painter.column import Column
from modules.data_updater.painter.text import Text
import os
from modules.data_updater.painter.united_cell import UnitedCell
from modules.database.group.group import Group


def update():
    for user in User.all():
        update_user(user)


def group_is_class_group(group: Group):
    if not group.parent:
        return False

    if not group.parent.parent:
        return False

    if group.parent.parent.id == Group(name="10 класс").id:
        return True
    if group.parent.parent.id == Group(name="11 класс").id:
        return True

    return False


def group_is_class(group: Group):
    if not group.parent:
        return False

    if group.parent.id == Group(name="10 класс").id:
        return True

    if group.parent.id == Group(name="11 класс").id:
        return True

    return False


def group_is_course(group: Group):
    if not group.parent:
        return False

    return group.parent.id == Group(name="Спецкурсы").id


def group_is_club(group: Group):
    if not group.parent:
        return False

    return group.parent.id == Group(name="Клубы").id


def group_is_academic_group(group: Group):
    if "группа" not in group.name:
        return False

    if not group.parent:
        return False

    if group.parent.id == Group(name="10 класс").id:
        return True

    if group.parent.id == Group(name="11 класс").id:
        return True

    return False


def update_user(user: User):
    dates = []
    for date in get_current_string_dates():
        events = user.date_events(date)
        for group in user.groups:
            if not group.parent:
                continue
            if group.parent.parent == Group(name="10 класс") or group.parent.parent == Group(name="11 класс"):
                pass

            if group.parent ==
                if group.parent == Group(name="10 ")

        if user.get_date_timetable(date=date):
            continue

        if not events:
            continue

        group = [event.group for event in events][0]

        relation_path = group.relation_path
        group = f"{relation_path[-2].name}  {relation_path[-1].name}"
        image = get_image(date, group, events)
        text = get_text(date, group, events)
        dates.append(date)

        user.insert_timetable(date, image, text)

    if not dates:
        return

    notif = user.notifications
    notif.append(f"Доступно расписание на {', '.join(dates)}")
    user.notifications = notif
    pass


def update_user_class(user: User):
    dates = []
    user_groups_ids = [group.id for group in user.groups]
    for date in get_current_string_dates():
        for group in user.groups:
            if not group_is_class(group):
                continue

            check = True
            for child in group.children:
                if child.id not in user_groups_ids:
                    check = False

            if check and not group_is_academic_group(group):
                relation_path = group.relation_path
                group = f"{relation_path[-2].name}  {relation_path[-1].name}"
                image = get_class_image(date, group)
                text = get_text(date, group, events)
                dates.append(date)

                user.insert_timetable(date, image, text)

            else:
                for child in group.children:
                    if child.id not in user_groups_ids:
                        continue

                    relation_path = group.relation_path
                    group = f"{relation_path[-2].name}  {relation_path[-1].name}"
                    image = get_image(date, group, child.get_date_events(date))
                    text = get_text(date, group, child.get_date_events(date))
                    dates.append(date)

                    user.insert_timetable(date, image, text)

    return dates


def update_user_clubs():
    pass


def normalize_string(string: str):
    MAX_LENGTH = 20
    lines = []
    cur_line = ""
    for word in string.split():
        if len(cur_line + " " + word) > MAX_LENGTH:
            if cur_line:
                lines.append(cur_line)
            cur_line = word
        else:
            cur_line += " " + word

    if cur_line:
        lines.append(cur_line)

    return lines


def normalize_value(value: str) -> str:
    lines = value.split("\n")
    result = []
    for line in lines:
        for new_line in normalize_string(line):
            result.append(new_line)

    return "\n".join(result)


def get_text(date, group, events):
    result = []
    result.append(f"{date} {group}")
    result.append(f"")
    for event in events:
        result.append(f"{event.start} - {event.end}")
        result.append(f"{event.name}")
        result.append(f"")

    return "\n".join(result)


def get_class_image(date, group: Group):
    children = group.children
    children_events = [child.get_date_events(date) for child in children]
    width = len(children) + 1
    height = max(len(events) for events in children_events) + 2
    content = [[None for _ in range(width)] for _ in range(height)]
    date = date.split(".")
    date = f"{date[0]}.{date[1]}\n{date[2]}"
    content[0][0] = Text(value=date, font="Roboto Black", size=30, fill="white")
    content[0][0]._horizontal_alignment = "center"

    content[0][1] = Text(value=group.name, font="Roboto Black", size=40, fill="white")
    content[0][2] = Text(value=group, font="Roboto Black", size=40, fill="white")
    time_intervals = []

    for events in children_events:
        for event in events:
            time_intervals.append(f"{event.start} - {event.end}")

    content[1][0] = Text(value="№", font="Roboto Black", size=40, fill="white")
    content[1][1] = Text(value=group.children[0].name, font="Roboto Black", size=40, fill="white")
    content[1][2] = Text(value=group.children[1].name, font="Roboto Black", size=40, fill="white")
    time_intervals = list(set(time_intervals))
    time_intervals.sort(key=lambda x: datetime.datetime.strptime(x.split('-')[0], "%H:%M"))
    for i in range(len(group.children)):
        event = group.children[i]
        ind = time_intervals.index(f"{event.start} - {event.end}")
        value = normalize_value(event.name)
        content[ind + 2][i + 1] = Text(value=value, font="Roboto Bold", size=30, fill="white")
        content[ind + 2][i + 1]._horizontal_alignment = "center"

    lesson_number = 1
    for i in range(2, height):
        if time_intervals[i - 2] == "00:00 - 00:00":
            lesson_number = 0

        start, end = time_intervals[i - 2].split(" - ")
        column = Column(outline_width=0)
        column._cell_space = -5
        column.add(Text(value=start, font="Roboto Black", size=20, fill="#424549"))
        column.add(Text(value=f"{lesson_number}", font="Roboto Black", size=40, fill="white"))
        column.add(Text(value=end, font="Roboto Black", size=20, fill="#424549"))
        content[i][0] = column
        lesson_number += 1

    table = Table(content=content, left_top=(10, 10))
    for i in range(2, table._height - 1):
        if content[i][1] and content[i + 1][1]:
            if content[i][1]._lines == content[i + 1][1]._lines:
                table.unite_cells((i, 1), (i + 1, 1))

        if content[i][2] and content[i + 1][2]:
            if content[i][2]._lines == content[i + 1][2]._lines:
                table.unite_cells((i, 2), (i + 1, 2))

    table.unite_cells((0, 1), (0, 2))
    for i in range(2, table._height):
        if not content[i][1] or not content[i][2]:
            continue

        if content[i][1]._lines == content[i][2]._lines:
            try:
                table.unite_cells((i, 1), (i, 2))
            except ValueError:
                pass

    table.squeeze()
    for i in range(table._height):
        for j in range(table._width):
            table[i][j].outline_width = 0

    table[0][0].pixels.padding = 10
    table[0][1].pixels.padding = 10
    # расписание
    for i in range(1, table._height):
        if not table._cell_is_active(table[i][1]):
            continue
        table[i][1].fill = "#424549"
        table[i][1].outline_color = "#36393e"
        table[i][1].pixels.padding = 20
        table[i][1].pixels.width = 400
        table[i][1].outline_width = 8
        table[i][1].horizontal_alignment = "center"
    # расписание
    for i in range(2, table._height):
        if not table._cell_is_active(table[i][1]):
            continue

        table[i][1].top_outline_width = 0

    # номера
    for i in range(0, table._height):
        table[i][0].fill = "#282b30"
        table[i][0].outline_color = "#36393e"
        table[i][0].pixels.padding = 0
        table[i][0].outline_width = 0

    table[0][0].fill = "#282b30"
    table[0][1].fill = "#282b30"
    image = Image.new('RGB', (table.pixels.width + 20, table.pixels.height + 20), "#282b30")
    canvas = ImageDraw.Draw(image)
    table.draw(canvas)

    image.save("img.png")
    with open("img.png", "rb") as f:
        image_content = f.read()
    os.remove("img.png")

    return image_content


def get_image(date, group, events):
    content = [[None for _ in range(2)] for _ in range(len(events) + 1)]
    date = date.split(".")
    date = f"{date[0]}.{date[1]}\n{date[2]}"
    content[0][0] = Text(value=date, font="Roboto Black", size=30, fill="white")
    content[0][0]._horizontal_alignment = "center"

    content[0][1] = Text(value=group, font="Roboto Black", size=40, fill="white")

    lesson_number = 1

    for event in events:
        if event.start == "00:00" and event.end == "00:00":
            lesson_number = 0

        if "ассамбл" in event.name.lower():
            lesson_number = 0
            break

    for i in range(1, len(events) + 1):
        column = Column(outline_width=0)
        column._cell_space = -5
        event = events[i - 1]
        column.add(Text(value=event.start, font="Roboto Black", size=20, fill="#424549"))
        column.add(Text(value=f"{lesson_number}", font="Roboto Black", size=40, fill="white"))
        column.add(Text(value=event.end, font="Roboto Black", size=20, fill="#424549"))
        content[i][0] = column
        lesson_number += 1

        value = normalize_value(event.name)
        content[i][1] = Text(value=value, font="Roboto Bold", size=30, fill="white")
        content[i][1]._horizontal_alignment = "center"

    table = Table(content=content, left_top=(10, 10))
    for i in range(1, table._height - 1):
        if content[i][1]._lines == content[i + 1][1]._lines:
            table.unite_cells((i, 1), (i + 1, 1))

    table.squeeze()
    for i in range(table._height):
        for j in range(table._width):
            table[i][j].outline_width = 0

    table[0][0].pixels.padding = 10
    table[0][1].pixels.padding = 10
    # расписание
    for i in range(1, table._height):
        if not table._cell_is_active(table[i][1]):
            continue
        table[i][1].fill = "#424549"
        table[i][1].outline_color = "#36393e"
        table[i][1].pixels.padding = 20
        table[i][1].pixels.width = 400
        table[i][1].outline_width = 8
        table[i][1].horizontal_alignment = "center"
    # расписание
    for i in range(2, table._height):
        if not table._cell_is_active(table[i][1]):
            continue

        table[i][1].top_outline_width = 0

    # номера
    for i in range(0, table._height):
        table[i][0].fill = "#282b30"
        table[i][0].outline_color = "#36393e"
        table[i][0].pixels.padding = 0
        table[i][0].outline_width = 0

    table[0][0].fill = "#282b30"
    table[0][1].fill = "#282b30"
    image = Image.new('RGB', (table.pixels.width + 20, table.pixels.height + 20), "#282b30")
    canvas = ImageDraw.Draw(image)
    table.draw(canvas)

    image.save("img.png")
    with open("img.png", "rb") as f:
        image_content = f.read()
    os.remove("img.png")

    return image_content


if __name__ == '__main__':
    update()
