from modules.files_api import parsed_files_path, downloads_path
import os
import openpyxl
from modules.database_updater.patterns import find_pattern, groups_patterns
from modules.database_updater.table import Table
from modules.database_api import Group, Event
from modules.database_api.interaction.fetch import *
from modules.database_api.interaction.insert import *


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

    os.replace(download_path, parsed_path)


def parse_sheet(sheet):
    table = Table(sheet)
    group_name = find_pattern(sheet.title, groups_patterns)
    group = fetch_class_group_by_name(group_name)
    groups_sequences = []

    # finding lessons number and time column
    lesson_number_col = table.find_cell_by_regular_pattern(r"^\s{0,}урок\s{0,}$")[1]
    time_col = table.find_cell_by_regular_pattern(r"^\s{0,}время\s{0,}$")[1]

    for row in range(table.height):
        for col in range(table.width):
            if find_pattern(table.matrix[row][col], groups_patterns):
                groups, events = get_sequence(table, lesson_number_col, time_col, row, col)
                groups.insert(0, group)
                groups_sequences.append((groups, events))

    return groups_sequences


def get_sequence(table, lesson_number_col, time_col, row, col):
    groups = []
    events = []
    while row < table.height:
        if table.matrix[row][lesson_number_col] == "None":
            break

        group_name = find_pattern(table.matrix[row][col], groups_patterns)

        if group_name is not None:
            groups.append(fetch_class_group_by_name(group_name))

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
    place = lines[-1]
    event = Event(name=name, about="None", date="None", start=start, end=end, owner=owner, place=place)
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
