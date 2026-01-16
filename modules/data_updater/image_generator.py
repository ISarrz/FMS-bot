import io
from PIL import ImageDraw, Image
from modules.data_updater.painter import Text, Column, colors, Table
from modules.data_updater.tools import EventsGroup, CategoryGroup, NodeGroup, normalize_value
from typing import List, Any, Tuple
from datetime import datetime


def height_dfs(root: NodeGroup):
    if isinstance(root, CategoryGroup) and root.children:
        return max(height_dfs(child) for child in root.children) + 1

    elif isinstance(root, EventsGroup):
        return len(root.events) + 1

    return 1


def width_dfs(root: NodeGroup):
    if isinstance(root, CategoryGroup) and root.children:
        return sum(width_dfs(child) for child in root.children)

    return 1


def time_intervals_dfs(root: NodeGroup, time_intervals: set):
    if isinstance(root, CategoryGroup):
        for child in root.children:
            time_intervals_dfs(child, time_intervals)

    elif isinstance(root, EventsGroup):
        for event in root.events:
            time_intervals.add((event.start, event.end))


def set_group_content(group: NodeGroup, table: Table, row, column, time_intervals: List[Tuple[str, str]]):
    if isinstance(group, CategoryGroup):
        for child in group.children:
            table[row][column].content = Text(value=group.title, font="Roboto Black", size=40, fill="white")
            set_group_content(child, table, row + 1, column, time_intervals)
            column += 1

    elif isinstance(group, EventsGroup):
        table[row][column].content = Text(value=group.title, font="Roboto Black", size=40, fill="white")
        event_ind = 0
        group_events = group.events
        for i in range(len(time_intervals)):
            event = group_events[event_ind]

            if (event.start, event.end) == time_intervals[i]:
                event_ind += 1

        for event in group.events:
            ind = time_intervals.index((event.start, event.end))
            table[row + ind + 1][column].content = Text(value=normalize_value(event.name), font="Roboto Bold", size=30,
                                                        fill="white")


def set_time_slots(table, time_intervals):
    row = table.height - len(time_intervals)
    column = 0
    for i in range(len(time_intervals)):
        content = Column(outline_width=0)
        content._cell_space = -5
        start = time_intervals[i][0]
        end = time_intervals[i][1]
        if start == "00:00" and end == "00:00":
            content = Text(value=f"{i + 1}", font="Roboto Black", size=40, fill="white")

        else:
            text = Text(value=start, font="Roboto Black", size=20, fill=colors["discord1"])
            content.add(text)

            text = Text(value=f"{i + 1}", font="Roboto Black", size=40, fill="white")
            content.add(text)

            text = Text(value=end, font="Roboto Black", size=20, fill=colors["discord1"])
            content.add(text)

        table[row + i][column].content = content


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


def get_timetable_image(root: NodeGroup, date: str):
    width = width_dfs(root) + 1
    height = height_dfs(root)

    content: List[List[Any]] = [[None for _ in range(width)] for _ in range(height)]
    table = Table(content=content, left_top=(10, 0))

    # date
    date = date.split(".")
    date = Text(value=f"{date[0]}.{date[1]}\n{date[2]}", font="Roboto Black", size=30, fill="white")
    table[0][0].content = date

    time_intervals = set()
    time_intervals_dfs(root, time_intervals)
    time_intervals = list(time_intervals)
    time_intervals.sort(key=lambda x: (datetime.strptime(x[0], "%H:%M"), datetime.strptime(x[1], "%H:%M")))

    set_time_slots(table, time_intervals)
    set_group_content(root, table, 0, 1, time_intervals)

    for row in range(height):
        for column in range(1, width - 1):
            if table[row][column].content and table[row][column + 1].content:
                if table[row][column].content.lines == table[row][column + 1].content.lines:
                    table.unite_cells((row, column), (row, column + 1))

    for column in range(1, width):
        for row in range(height - 1):
            if table[row][column].content and table[row + 1][column].content:
                if table[row][column].content.lines == table[row + 1][column].content.lines:
                    table.unite_cells((row, column), (row + 1, column))

    groups_height = height - len(time_intervals)
    if groups_height > 1:
        table[1][0].content = Text(value="№", font="Roboto Black", size=40, fill="white")

    # time slots
    for row in range(height):
        table[row][0].outline_width = 0

        if table[row][0].content:
            table[row][0].content.horizontal_alignment = "center"
            table[row][0].content.vertical_alignment = "center"

        table[row][0].pixels.padding = -5
        table[row][0].horizontal_alignment = "center"
        table[row][0].vertical_alignment = "center"

    # events
    for row in range(groups_height, height):
        for column in range(1, width):
            if table[row][column].content:
                table[row][column].content.horizontal_alignment = "center"
            table[row][column].fill = colors["discord1"]
            table[row][column].outline_color = colors["discord2"]
            table[row][column].pixels.padding = 10
            table[row][column].outline_width = 5
            table[row][column].horizontal_alignment = "center"

    table.squeeze()
    table[0][0].pixels.width = 60
    table[0][0].pixels.padding = 2

    # groups
    for row in range(groups_height):
        for column in range(1, width):
            if table[row][column].content:
                table[row][column].content.horizontal_alignment = "center"
                table[row][column].content.vertical_alignment = "center"

            table[row][column].fill = colors["discord3"]
            table[row][column].pixels.padding = 5
            table[row][column].outline_width = 0
            table[row][column].pixels.height = 20
            table[row][column].pixels.width *= 1.1
            table[row][column].horizontal_alignment = "center"
            table[row][column].vertical_alignment = "center"

    image = Image.new('RGB', (table.pixels.width + 20, table.pixels.height + 20), "#282b30")
    canvas = ImageDraw.Draw(image)
    table.draw(canvas)

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    image_content = img_byte_arr.getvalue()

    return image_content
