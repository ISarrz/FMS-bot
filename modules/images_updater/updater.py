import os
from modules.database_api import *
from modules.time import *
from modules.images_updater.table import *
from modules.images_updater.style import *
from modules.images_updater.table_parts import *
import datetime as dt
from modules.files_api import *


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
                                   start=event['start'], end=event['end'],owner= event['owner'], place=event['place'])
                           for event in group_events]

        if group_events:
            render_group(db_group, db_group_events)
            groups_with_events.append(db_group)



def render_group(group: DbGroup, events):
    event = events[0]
    events.sort(key=lambda ev: dt.datetime.strptime(ev.start, "%H:%M").date())

    # time | events | place
    width = 3

    # sequences
    header = [[event.date, group.name, '']]
    matrix = header + [[''] * width for row in range(len(events))]

    for i in range(len(events)):
        event_number = i + 1
        matrix[event_number][0] = f"{event.start}\n{event_number}\n{event.end}"
        matrix[event_number][1] = f"{event.name}\n{event.owner}\n{event.about}"
        matrix[event_number][2] = f"{event.place}"

    table = Table(matrix=matrix, cell_style=main_style)
    table.set_area_style((0, 1), (0, len(matrix[0]) - 1), header_style)

    table.set_area_style((1, 0), (len(matrix) - 1, 0), numbers_style)
    # table.set_cell_style((0, 0), empty_style)
    table.set_cell_style((0, 0), date_style)
    # lines_styles = [time_text, numbers_text, time_text]
    # table.set_area_lines_style((2, 0), (len(matrix) - 1, 0), lines_styles)
    # table.unite_area((0, 1), (0, len(matrix[0]) - 1))

    # table.set_same_columns(list(range(1, len(matrix[0]))))
    # for i in range(2, len(matrix)):
    #     for j in range(1, len(matrix[i]) - 1):
    #         if matrix[i][j] == matrix[i][j + 1]:
    #             table.unite_cells((i, j), (i, j + 1))
    # for i in range(2, len(matrix) - 1):
    #     for j in range(1, len(matrix[i])):
    #         if matrix[i][j] == matrix[i + 1][j]:
    #             try:
    #                 table.unite_cells((i, j), (i + 1, j))
    #             except Exception:
    #                 pass

    table.autoformat()
    picture = table.draw(margin=10)


    picture.save(images_updater_path + "/img.png")


if __name__ == '__main__':
    update()
