from modules.files_api import parsed_files_path, downloads_path
import os
import openpyxl
from modules.database_updater.patterns import find_pattern, groups_patterns
from modules.database_updater.table import Table
from modules.database_api import *
from modules.logger import *


@logger
def parse_all():
    for file_name in os.listdir(downloads_path):
        parse_file(file_name)


def parse_file(file_name):
    download_path = os.path.join(downloads_path, file_name)
    parsed_path = os.path.join(parsed_files_path, file_name)
    date = file_name.replace(".xlsx", "")
    workbook = openpyxl.load_workbook(download_path)
    for sheet_name in workbook.sheetnames:
        pattern = find_pattern(sheet_name, groups_patterns)
        if pattern is not None:
            sheet = workbook[sheet_name]
            groups_sequences = parse_sheet(sheet)

            # setting date for events
            for groups, events in groups_sequences:
                for event in events:
                    event.date = date

            insert_into_database(groups_sequences)

    os.replace(download_path, parsed_path)


def parse_sheet(sheet):
    table = Table(sheet)
    # parent_group_name = find_pattern(sheet.title, groups_patterns)
    # parent_group = fetch_class_group_by_name(parent_group_name)
    groups_sequences = []

    # finding lessons number and time column
    lesson_number_col = table.find_cell_by_regular_pattern(r"^\s{0,}урок\s{0,}$")[1]
    time_col = table.find_cell_by_regular_pattern(r"^\s{0,}время\s{0,}$")[1]

    for row in range(table.height):
        for col in range(table.width):
            if find_pattern(table.matrix[row][col], groups_patterns):
                groups, events = get_sequence(table, sheet, lesson_number_col, time_col, row, col)
                if (groups, events) not in groups_sequences:
                    groups_sequences.append((groups, events))

    return groups_sequences


def get_sequence(table, sheet, lesson_number_col, time_col, row, col):
    school_group = 'ФМШ'
    sheet_group = find_pattern(sheet.title, groups_patterns)
    groups = [
        fetch_class_group_by_name(school_group),
        fetch_class_group_by_name(sheet_group)
    ]
    group_name = find_pattern(table.matrix[row][col], groups_patterns)

    if 'группа' in group_name:
        gr = fetch_group_by_name_and_parent_id("Академическая группа", groups[-1].id)
        groups.append(fetch_class_group_by_id(gr['id']))

    events = []
    while row < table.height:
        if table.matrix[row][lesson_number_col] == "None":
            break

        group_name = find_pattern(table.matrix[row][col], groups_patterns)

        if group_name is not None:
            if len(groups) == 0:
                groups.append(fetch_class_group_by_name(group_name))

            elif groups[-1].name != group_name:
                parent_id = groups[-1].id
                group = fetch_group_by_name_and_parent_id(group_name, parent_id)
                groups.append(DbGroup(id=group['id'], name=group['name'], about=group['about']))

        else:
            time = table.matrix[row][time_col]
            event = parse_event(time, table.matrix[row][col])
            events.append(event)

        table.matrix[row][col] = "None"

        row += 1

    return groups, events


def parse_event(time, value):
    start, end = time.replace(".", ":").split("-")
    start = start.strip()
    end = end.strip()
    lines = value.split("\n")
    name = lines[0]
    owner = "\n".join(lines[1:-1]) if lines[1:-1] else "None"
    about = value
    place = lines[-1]
    event = Event(name=name, about=about, date="None", start=start, end=end, owner=owner, place=place)
    return event


def insert_into_database(groups_sequences):
    for groups, events in groups_sequences:

        for event in events:
            # adding event in database
            event_id = insert_class_event(event)

            # adding event relation
            insert_group_event(groups[-1].id, event_id)


if __name__ == '__main__':
    parse_all()
