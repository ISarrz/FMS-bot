import os
from io import BytesIO

from modules.database_api import *
from modules.time import *
from modules.images_updater.table import *
from modules.images_updater.style import *
from modules.images_updater.table_parts import *
import datetime as dt
from modules.files_api import *
from modules.logger.logger import logger, async_logger


@logger
def update():
    current_string_dates = get_current_string_dates()
    for date in current_string_dates:
        update_date(date)


def update_date(date: str):
    groups = fetch_all_groups()
    groups_with_events = []
    for group in groups:
        db_group = DbGroup(id=group['id'], name=group['name'], about=group['about'])
        group_events = fetch_group_events_by_group_id_and_date(db_group.id, date)

        db_group_events = [DbEvent(id=event['id'], name=event['name'], about=event['about'], date=event['date'],
                                   start=event['start'], end=event['end'], owner=event['owner'], place=event['place'])
                           for event in group_events]

        if group_events:
            render_group(db_group, db_group_events)

        groups_with_events.append(db_group)


def normalize_string(s):
    max_width = 40
    lines = []
    for line in s.split('\n'):
        if len(line) > max_width:
            new_line = []
            cur = ""
            for word in line.split():
                if len(cur + " " + word) > max_width:
                    new_line.append(cur)
                    cur = ""
                cur += " " + word
            if cur:
                new_line.append(cur)

            new_line = '\n'.join(new_line)
            lines.append(new_line)

        else:
            lines.append(line)

    response = '\n'.join(lines)
    return response


def render_group(group: DbGroup, events):
    default_event = events[0]
    events.sort(key=lambda ev: dt.datetime.strptime(ev.start, "%H:%M"))

    # time | events | place
    width = 2

    group_parent = fetch_parent_by_id(group.id)

    if group_parent:
        if len(f"{group_parent['name']} {group.name}") > 20:
            header = [[default_event.date, group_parent['name'] + "\n" + group.name]]
        else:
            header = [[default_event.date, group_parent['name'] + " " + group.name]]

    else:
        header = [[default_event.date, group.name]]

    # sequences
    matrix = header + [[''] * width for row in range(len(events))]

    for i in range(len(events)):
        event_number = i + 1
        matrix[event_number][0] = f"{events[i].start}\n{event_number}\n{events[i].end}"
        matrix[event_number][1] = normalize_string(events[i].about)

    table = Table(matrix=matrix, cell_style=main_style)

    table.set_area_style((0, 1), (0, 1), header_style)

    table.set_area_style((1, 0), (len(matrix) - 1, 0), numbers_style)
    # table.set_cell_style((0, 0), empty_style)
    table.set_cell_style((0, 0), date_style)

    lines_styles = [time_text, numbers_text, time_text]
    table.set_area_lines_style((1, 0), (len(matrix) - 1, 0), lines_styles)

    for i in range(2, len(matrix)):
        for j in range(1, len(matrix[i])):
            if matrix[i][j] == "None" or matrix[i][j] is None:
                matrix[i][j] = ''
                table.set_cell_style((i, j), black_empty_style)

    table.autoformat()
    picture = table.draw(margin=10)

    picture.save("img.png")
    with open("img.png", "rb") as f:
        image_content = f.read()

    os.remove("img.png")

    # image_content.seek(0)
    group_id = group.id
    date = events[0].date
    if not fetch_image_id_by_date_and_group_id(date, group_id):
        insert_image(date=date, group_id=group_id, image=image_content)


if __name__ == '__main__':
    update()
