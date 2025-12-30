from dataclasses import dataclass

from telegram import Update
from telegram.ext import CallbackContext
from modules.database.group.group import Group
from modules.config.paths import data_statistics_path
from modules.database.user.user import User
import json
import os


class Statistic:
    @property
    def users_count(self):
        return self.get_field("users_count")

    @users_count.setter
    def users_count(self, value):
        self.set_field("users_count", value)

    @property
    def eleven_grade_count(self):
        return Statistic.get_field("eleven_grade_count")

    @eleven_grade_count.setter
    def eleven_grade_count(self, value):
        Statistic.set_field("eleven_grade_count", value)

    @property
    def ten_grade_count(self):
        return Statistic.get_field("ten_grade_count")

    @ten_grade_count.setter
    def ten_grade_count(self, value):
        Statistic.set_field("ten_grade_count", value)

    @property
    def timetable_count(self):
        return Statistic.get_field("timetable_count")

    @timetable_count.setter
    def timetable_count(self, value: int):
        Statistic.set_field("timetable_count", value)

    @property
    def errors_count(self):
        return Statistic.get_field("errors_count")

    @errors_count.setter
    def errors_count(self, value):
        Statistic.set_field("errors_count", value)

    @staticmethod
    def get_field(field_name: str):
        with open(data_statistics_path) as f:
            response = json.load(f)

        return response[field_name]

    @staticmethod
    def set_field(field_name: str, value):
        data = dict()
        with open(data_statistics_path) as f:
            data = json.load(f)

        data[field_name] = value
        with open(data_statistics_path, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def reset():
        Statistic.users_count = 0
        Statistic.eleven_grade_count = 0
        Statistic.ten_grade_count = 0

    @staticmethod
    def get_group_count(group_name: str):
        return Statistic.get_field(group_name)

    @staticmethod
    def set_group_count(group_name: str):
        Statistic.set_field(group_name, group_name)

    @staticmethod
    def contains(value:str):
        data = dict()
        with open(data_statistics_path) as f:
            data = json.load(f)

        if data.__contains__(value):
            return True

        return False

    @staticmethod
    def initialize_():
        Statistic.set_field("users_count", 0)
        Statistic.set_field( "eleven_grade_count", 0)
        Statistic.set_field( "ten_grade_count", 0)
        Statistic.set_field( "timetable_count", 0)
        Statistic.set_field( "error_count", 0)

        for group in Group(name="10 класс").children + Group(name="11 класс").children:
            if "группа" in group.name:
                continue

            name = group.name

            Statistic.set_field(name, 0)



    @staticmethod
    def update():
        Statistic.initialize_()

        for user in User.all():
            groups = user.groups
            for group in groups:
                if group.name in data.keys():
                    if "группа" in group.name:
                        continue

                    name = group.name

                    count = get_statistics_field(name)
                    set_statistics_field(name, count + 1)

        data = get_statistics()
        set_statistics_field("ФМШ", data["11 класс"] + data["10 класс"])




if __name__ == "__main__":
    Statistic.users_count = 1

    # set_statistics_field("name", "123")
