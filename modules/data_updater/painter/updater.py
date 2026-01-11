import datetime

from sympy.codegen.ast import continue_

from modules.database.timetable.timetable import Timetable, TimetableNotFoundError
from modules.database.user.user import User
from modules.time.dates import get_current_string_dates
from PIL import ImageDraw, Image
from modules.data_updater.painter.containers.table.table import Table
from modules.data_updater.painter.containers.column import Column
from modules.data_updater.painter.containers.text import Text
import os
from modules.database.group.group import Group
from modules.data_updater.painter.constants import colors


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


def get_user_clubs(user: User):
    user_groups_ids = [group.id for group in user.groups]
    clubs = Group(name="Клубы").children
    result = []
    for club in clubs:
        if club.id in user_groups_ids:
            result.append(club)

    return result


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
        for group in user.groups:
            if group_is_academic_group(group):
                dates += update_user_academic_group(user, group, date)

            elif group_is_class(group):
                dates += update_user_class(user, group, date)

        dates += update_user_clubs(user, date)

    if not dates:
        return

    notif = [notification.value for notification in user.notifications]
    print(notif)
    notif.append(f"Доступно расписание на {', '.join(dates)}")
    print(notif)
    user.notifications = notif
    pass


def update_user_academic_group(user: User, group: Group, date: str):
    image = get_user_academic_group_image(user, group, date)
    text = get_user_class_group_text(user, group, date)

    if image:
        try:
            Timetable(date=date, image=image, text=text)

        except TimetableNotFoundError:
            user.insert_timetable(date=date, image=image, text=text)
            return [date]
    return []


def user_in_all_subgroups(user: User, group: Group):
    user_groups_ids = set([user_group.id for user_group in user.groups])
    children_ids = set([child.id for child in group.children])

    return children_ids.issubset(user_groups_ids)


def update_user_class(user: User, group: Group, date: str):
    dates = []
    if user_in_all_subgroups(user, group):
        image = get_user_class_image(user, group, date)
        text = get_user_class_text(user, group, date)
        if image:
            try:
                Timetable(date=date, image=image, text=text)

            except TimetableNotFoundError:
                user.insert_timetable(date=date, image=image, text=text)
                dates.append(date)

    else:
        user_groups_ids = [user_group.id for user_group in user.groups]
        for child in group.children:
            if child.id not in user_groups_ids:
                continue

            image = get_user_class_group_image(user, child, date)
            text = get_user_class_group_text(user, child, date)
            if image:
                try:
                    Timetable(date=date, image=image, text=text)

                except TimetableNotFoundError:
                    user.insert_timetable(date=date, image=image, text=text)
                    dates.append(date)

    dates = list(set(dates))
    return dates


def get_user_class_text(user: User, group: Group, date: str):
    result = []
    result.append(f"{date} {group.name}\n")
    for child in group.children:
        result.append(get_user_class_group_text(user, child, date))

    return "\n".join(result)


def get_user_class_group_text(user: User, group: Group, date: str):
    events = []
    events += group.get_date_events(date)
    events += get_user_courses_events(user, date)

    result = []
    result.append(f"{date} {group.parent.name} {group.name}")
    result.append(f"")
    for event in events:
        result.append(f"{event.start} - {event.end}")
        result.append(f"{event.name}")
        result.append(f"")

    return "\n".join(result)


def get_user_class_image(user: User, group: Group, date: str):
    events = []
    for child in group.children:
        events += child.get_date_events(date)

    events += get_user_courses_events(user, date)
    if not events:
        return None

    time_intervals = list(set([f"{event.start} - {event.end}" for event in events]))
    time_intervals.sort(key=lambda x: datetime.datetime.strptime(x.split(" - ")[0], "%H:%M"))

    events.sort(key=lambda event: datetime.datetime.strptime(event.start, "%H:%M"))

    content = [[None for _ in range(3)] for _ in range(len(events) + 2)]
    str_date = date.split(".")
    str_date = f"{str_date[0]}.{str_date[1]}\n{str_date[2]}"
    content[0][0] = Text(value=str_date, font="Roboto Black", size=30, fill="white")

    content[0][1] = Text(value=f"{group.parent.name} {group.name}", font="Roboto Black", size=40, fill="white")
    content[0][2] = Text(value=f"{group.parent.name} {group.name}", font="Roboto Black", size=40, fill="white")
    content[1][0] = Text(value=f"№", font="Roboto Black", size=40, fill="white")

    for i in range(len(group.children)):
        child = group.children[i]
        content[1][i + 1] = Text(value=child.name, font="Roboto Black", size=40, fill="white")

    # события по подгруппам
    for i in range(len(group.children)):
        child = group.children[i]
        for event in child.get_date_events(date):
            ind = time_intervals.index(f"{event.start} - {event.end}")
            content[ind + 2][i + 1] = Text(value=event.name, font="Roboto Bold", size=30, fill="white")

    # спецкурсы
    for event in get_user_courses_events(user, date):
        ind = time_intervals.index(f"{event.start} - {event.end}")
        for i in range(len(group.children)):
            content[ind + 2][i + 1] = Text(value=event.name, font="Roboto Bold", size=30, fill="white")

    # время и номер события
    lesson_number = 1
    for event in events:
        if "ассам" in event.name.lower():
            lesson_number = 0

    for i in range(len(time_intervals)):
        start, end = time_intervals[i].split(" - ")
        if start == "00:00" and end == "00:00":
            lesson_number = 0

        column = Column(outline_width=0)
        column._cell_space = -5

        column.add(Text(value=start, font="Roboto Black", size=20, fill=colors["discord1"]))
        column.add(Text(value=f"{lesson_number}", font="Roboto Black", size=40, fill="white"))
        column.add(Text(value=end, font="Roboto Black", size=20, fill=colors["discord1"]))
        content[i + 2][0] = column

        lesson_number += 1

    for i in range(len(content)):
        for j in range(len(content[0])):
            if isinstance(content[i][j], Text):
                content[i][j].horizontal_alignment = "center"

    while content:
        ind = len(content) - 1
        if content[ind][1] is None and content[ind][2] is None:
            content.pop()
        else:
            break

    table = Table(content=content, left_top=(10, 10))
    for i in range(2, table.height - 1):
        if content[i][1] is not None and content[i + 1][1] is not None:
            if content[i][1]._lines == content[i + 1][1]._lines:
                table.unite_cells((i, 1), (i + 1, 1))

        if content[i][2] is not None and content[i + 1][2] is not None:
            if content[i][2]._lines == content[i + 1][2]._lines:
                table.unite_cells((i, 2), (i + 1, 2))

    for i in range(0, table.height):
        if content[i][1] is not None and content[i][2] is not None:
            if content[i][1]._lines == content[i][2]._lines:
                pass
                try:
                    table.unite_cells((i, 1), (i, 2))

                except IndexError:
                    pass

    table.squeeze()
    for i in range(table.height):
        for j in range(table.width):
            table[i][j].outline_width = 0

    table[0][0].pixels.padding = 10
    table[0][1].pixels.padding = 10

    table[1][1].pixels.padding = 10
    # table[1][1].outline_width = 5
    # table[1][1].top_outline_width = 2
    # table[1][1].outline_color = colors["discord2"]

    # table[1][2].outline_width = 5
    # table[1][2].top_outline_width = 2
    # table[1][2].outline_color = colors["discord2"]
    table[1][2].pixels.padding = 10
    # table[1][1].outline_width = 8

    # расписание
    for i in range(2, table.height):
        for j in range(len(group.children)):
            if not table._cell_is_active(table[i][j + 1]):
                continue

            table[i][j + 1].fill = colors["discord1"]
            table[i][j + 1].outline_color = colors["discord2"]
            table[i][j + 1].pixels.padding = 20
            table[i][j + 1].pixels.width = 300
            table[i][j + 1].outline_width = 8
            table[i][j + 1].horizontal_alignment = "center"
            table[i][j + 1].top_outline_width = 0

    # номера
    for i in range(0, table.height):
        table[i][0].fill = colors["discord3"]
        table[i][0].outline_color = colors["discord2"]
        table[i][0].pixels.padding = 0
        table[i][0].outline_width = 0

    table[0][0].fill = colors["discord3"]
    table[0][1].fill = colors["discord3"]
    image = Image.new('RGB', (table.pixels.width + 20, table.pixels.height + 20), colors["discord3"])
    canvas = ImageDraw.Draw(image)
    table.draw(canvas)

    image.save("img.png")
    with open("img.png", "rb") as f:
        image_content = f.read()
    os.remove("img.png")
    # image.show()

    return image_content


def get_user_class_group_image(user: User, group: Group, date: str):
    events = group.get_date_events(date) + get_user_courses_events(user, date)
    if not events:
        return None

    events.sort(key=lambda event: datetime.datetime.strptime(event.start, "%H:%M"))

    content = [[None for _ in range(2)] for _ in range(len(events) + 1)]
    date = date.split(".")
    date = f"{date[0]}.{date[1]}\n{date[2]}"
    content[0][0] = Text(value=date, font="Roboto Black", size=30, fill="white")
    content[0][0]._horizontal_alignment = "center"

    content[0][1] = Text(value=f"{group.parent.name} {group.name}", font="Roboto Black", size=40, fill="white")

    lesson_number = 1

    for i in range(1, len(events) + 1):
        event = events[i - 1]

        if event.start == "00:00" and event.end == "00:00" or "ассамбл" in event.name.lower():
            lesson_number = 0

        column = Column(outline_width=0)
        column._cell_space = -5

        column.add(Text(value=event.start, font="Roboto Black", size=20, fill=colors["discord1"]))
        column.add(Text(value=f"{lesson_number}", font="Roboto Black", size=40, fill="white"))
        column.add(Text(value=event.end, font="Roboto Black", size=20, fill=colors["discord1"]))
        content[i][0] = column

        value = normalize_value(event.name)
        content[i][1] = Text(value=value, font="Roboto Bold", size=30, fill="white")
        content[i][1]._horizontal_alignment = "center"

        lesson_number += 1

    table = Table(content=content, left_top=(10, 10))
    for i in range(1, table.height - 1):
        if content[i][1]._lines == content[i + 1][1]._lines:
            table.unite_cells((i, 1), (i + 1, 1))

    table.squeeze()
    for i in range(table.height):
        for j in range(table.width):
            table[i][j].outline_width = 0

    table[0][0].pixels.padding = 10
    table[0][1].pixels.padding = 10

    # расписание
    for i in range(1, table.height):
        if not table._cell_is_active(table[i][1]):
            continue
        table[i][1].fill = colors["discord1"]
        table[i][1].outline_color = colors["discord2"]
        table[i][1].pixels.padding = 20
        table[i][1].pixels.width = 400
        table[i][1].outline_width = 8
        table[i][1].horizontal_alignment = "center"
    # расписание
    for i in range(2, table.height):
        if not table._cell_is_active(table[i][1]):
            continue

        table[i][1].top_outline_width = 0

    # номера
    for i in range(0, table.height):
        table[i][0].fill = colors["discord3"]
        table[i][0].outline_color = colors["discord2"]
        table[i][0].pixels.padding = 0
        table[i][0].outline_width = 0

    table[0][0].fill = colors["discord3"]
    table[0][1].fill = colors["discord3"]
    image = Image.new('RGB', (table.pixels.width + 20, table.pixels.height + 20), colors["discord3"])
    canvas = ImageDraw.Draw(image)
    table.draw(canvas)

    image.save("img.png")
    with open("img.png", "rb") as f:
        image_content = f.read()
    os.remove("img.png")
    # image.show()

    return image_content


def get_user_academic_group_image(user: User, group: Group, date: str):
    return get_user_class_group_image(user, group, date)


def get_user_clubs_text(user: User, date: str):
    clubs = get_user_clubs(user)
    events = []
    for club in clubs:
        event = club.get_date_events(date)
        if event:
            events += event

    events.sort()

    result = []
    result.append(f"{date} Клубы")
    result.append(f"")
    for event in events:
        result.append(f"{event.start} - {event.end}")
        result.append(f"{event.name}")
        result.append(f"")

    return "\n".join(result)


def get_user_clubs_image(user: User, date: str):
    clubs = get_user_clubs(user)
    events = []
    for club in clubs:
        event = club.get_date_events(date)
        if event:
            events += event

    events.sort()

    if not events:
        return None


    content = [[None for _ in range(2)] for _ in range(len(events) + 1)]
    date = date.split(".")
    date = f"{date[0]}.{date[1]}\n{date[2]}"
    content[0][0] = Text(value=date, font="Roboto Black", size=30, fill="white")
    content[0][0]._horizontal_alignment = "center"

    content[0][1] = Text(value=f"Клубы", font="Roboto Black", size=40, fill="white")

    for i in range(1, len(events) + 1):
        event = events[i - 1]
        column = Column(outline_width=0)
        column._cell_space = -5

        column.add(Text(value=event.start, font="Roboto Black", size=20, fill=colors["discord1"]))
        column.add(Text(value=f"{i}", font="Roboto Black", size=40, fill="white"))
        column.add(Text(value=event.end, font="Roboto Black", size=20, fill=colors["discord1"]))
        content[i][0] = column

        value = normalize_value(event.name)
        content[i][1] = Text(value=value, font="Roboto Bold", size=30, fill="white")
        content[i][1]._horizontal_alignment = "center"

    table = Table(content=content, left_top=(10, 10))
    for i in range(1, table.height - 1):
        if content[i][1]._lines == content[i + 1][1]._lines:
            table.unite_cells((i, 1), (i + 1, 1))

    table.squeeze()
    for i in range(table.height):
        for j in range(table.width):
            table[i][j].outline_width = 0

    table[0][0].pixels.padding = 10
    table[0][1].pixels.padding = 10

    # расписание
    for i in range(1, table.height):
        if not table._cell_is_active(table[i][1]):
            continue
        table[i][1].fill = colors["discord1"]
        table[i][1].outline_color = colors["discord2"]
        table[i][1].pixels.padding = 20
        table[i][1].pixels.width = 400
        table[i][1].outline_width = 8
        table[i][1].horizontal_alignment = "center"
    # расписание
    for i in range(2, table.height):
        if not table._cell_is_active(table[i][1]):
            continue

        table[i][1].top_outline_width = 0

    # номера
    for i in range(0, table.height):
        table[i][0].fill = colors["discord3"]
        table[i][0].outline_color = colors["discord2"]
        table[i][0].pixels.padding = 0
        table[i][0].outline_width = 0

    table[0][0].fill = colors["discord3"]
    table[0][1].fill = colors["discord3"]
    image = Image.new('RGB', (table.pixels.width + 20, table.pixels.height + 20), colors["discord3"])
    canvas = ImageDraw.Draw(image)
    table.draw(canvas)

    image.save("img.png")
    with open("img.png", "rb") as f:
        image_content = f.read()
    os.remove("img.png")
    # image.show()

    return image_content


def get_user_courses_events(user: User, date: str):
    result = []
    for group in user.groups:
        if not group_is_course(group):
            continue

        events = group.get_date_events(date)
        result += events

    return result


def update_user_clubs(user: User, date: str):
    image = get_user_clubs_image(user, date)
    text = get_user_clubs_text(user, date)
    if image:
        try:
            Timetable(date=date, image=image, text=text)

        except TimetableNotFoundError:
            user.insert_timetable(date=date, image=image, text=text)
            return [date]

    return []


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
    # for i in range(1, table._height - 1):
    #     if content[i][1]._lines == content[i + 1][1]._lines:
    #         table.unite_cells((i, 1), (i + 1, 1))

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
