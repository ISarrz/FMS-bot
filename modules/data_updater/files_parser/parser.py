from modules.config.paths import parsed_files_path, downloaded_files_path
import os
import openpyxl
from modules.data_updater.files_parser.patterns import (
    find_pattern, groups_patterns, events_name_patterns,
    events_owner_patterns, events_place_patterns, find_all_patterns)

from modules.data_updater.files_parser.table import Table
from modules.database import *
# from modules.logger.logger import logger, async_logger
from modules.database.group.group import GroupNotFoundError
from modules.database.event.event import Event, CnEvent, EventAlreadyExistsError
from datetime import datetime


class Parser:
    def parse_all(self):
        for file_name in os.listdir(downloaded_files_path):
            self.parse_file(file_name)

    def parse_file(self, file_name):
        downloaded_file_path = os.path.join(downloaded_files_path, file_name)
        parsed_path = os.path.join(parsed_files_path, file_name)
        self.date = file_name.replace(".xlsx", "")
        workbook = openpyxl.load_workbook(downloaded_file_path)
        for sheet_name in workbook.sheetnames:
            if not find_pattern(sheet_name, groups_patterns):
                continue

            self.sheet = workbook[sheet_name]
            self.parse_sheet()

        os.replace(downloaded_file_path, parsed_path)

    def parse_sheet(self):
        self.table = Table(self.sheet)
        self.time_col = self.table.find_cell_by_regular_pattern(r"^\s{0,}время\s{0,}$")[1]

        for row in range(self.table.height):
            for col in range(self.table.width):
                if not find_pattern(self.table.matrix[row][col], groups_patterns):
                    continue

                self.parse_group(row, col)

    def parse_group(self, row, col):
        parent_name = find_pattern(self.sheet.title, groups_patterns)
        parent = Group(name=parent_name)

        for row in range(row, self.table.height):
            cur_cell = self.table.matrix[row][col]

            group_name = find_pattern(cur_cell, groups_patterns)

            if parent.name == group_name or not cur_cell:
                self.table.matrix[row][col] = ""
                continue

            try:
                parent = Group(name=group_name, parent=parent)
                self.table.matrix[row][col] = ""

            except GroupNotFoundError:
                break

        events = self.parse_events(row, col)
        pass
        for event in events:
            try:
                Event.insert(name=event.name, group_id=parent.id, date=event.date, start=event.start, end=event.end,
                             owner=event.owner, place=event.place)
            except EventAlreadyExistsError:
                pass

    def parse_events(self, row, col):
        events = []

        for row in range(row, self.table.height):
            cur_cell = self.table.matrix[row][col]
            self.table.matrix[row][col] = ""

            if not cur_cell:
                continue

            if find_pattern(cur_cell, groups_patterns):
                break

            time = self.table.matrix[row][self.time_col]
            event = self.parse_event(time, cur_cell)
            events.append(event)

        return events

    def parse_event(self, time, value):

        try:
            start, end = time.split("-")
            start = datetime.strptime(start.strip(), "%H.%M").strftime("%H:%M")
            end = datetime.strptime(end.strip(), "%H.%M").strftime("%H:%M")
        except Exception:
            start = ""
            end = ""

        name = value
        event = CnEvent(name=name, group_id=-1, date=self.date, start=start, end=end, owner="", place="")

        return event

        name = find_pattern(value, events_name_patterns)

        owner = "\n".join(find_all_patterns(value, events_owner_patterns))
        if not owner:
            owner = ""
        place = "\n".join(find_all_patterns(value, events_place_patterns))
        if not place:
            place = ""

        if name == "Ассамблея":
            start = "08:00"
            end = "08:25"
        if name:
            event = CnEvent(name=name, group_id=-1, date=self.date, start=start, end=end, owner=owner, place=place)
        else:
            event = CnEvent(name=value, group_id=-1, date=self.date, start=start, end=end, owner="", place="")
        # ab = [event.name, event.owner, event.place]

        return event


if __name__ == '__main__':
    Parser().parse_all()
