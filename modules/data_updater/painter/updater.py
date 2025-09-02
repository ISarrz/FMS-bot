from modules.database.user.user import User
from modules.database.event.event import Event
from modules.time.dates import get_current_string_dates
from PIL import ImageFont, ImageDraw, Image
from modules.data_updater.painter.table import Table
from modules.data_updater.painter.column import Column
from modules.data_updater.painter.text import Text
import os


def update():
    for user in User.all():
        update_user(user)


def update_user(user: User):
    dates = []
    for date in get_current_string_dates():
        events = user.date_events(date)

        if user.get_date_timetable(date=date):
            continue
        if not events:
            continue
        group = [event.group for event in events][0]
        relation_path = group.relation_path
        group = f"{relation_path[-2].name}  {relation_path[-1].name}"
        image = get_image(date, group, events)
        dates.append(date)

        user.insert_timetable(date, image)

    if not dates:
        return
    notifications = user.notifications
    notifications.append(f"Доступно расписание на {(', ').join(dates)}")
    user.notifications = notifications


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


def get_image(date, group, events):
    content = [[None for _ in range(2)] for _ in range(len(events) + 1)]
    date = date.split(".")
    date = f"{date[0]}.{date[1]}\n{date[2]}"
    content[0][0] = Text(value=date, font="Roboto Black", size=30, fill="white")
    content[0][0]._horizontal_alignment = "center"

    content[0][1] = Text(value=group, font="Roboto Black", size=40, fill="white")
    lesson_number = 1
    try:
        if "ассамбл" in content[1][1].lower():
            lesson_number = 0
    except Exception as e:
        pass

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
