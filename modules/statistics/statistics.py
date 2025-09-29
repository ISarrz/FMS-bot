from telegram import Update
from telegram.ext import CallbackContext
from modules.database.group.group import Group
from modules.config.paths import data_statistics_path
from modules.database.user.user import User
import json
import os


def get_statistics():
    with open(data_statistics_path) as f:
        response = json.load(f)

    return response


def get_statistics_field(field):
    return get_statistics()[field]


def set_statistics_field(field, value):
    data = dict()
    with open(data_statistics_path) as f:
        data = json.load(f)

    data[field] = value
    with open(data_statistics_path, "w") as f:
        json.dump(data, f, indent=4)


def update_statistics():
    data = get_statistics()

    for user in User.all():
        groups = user.groups
        for group in groups:
            if group.name in data.keys():
                if "группа" in group.name:
                    name = group.parent.name + " " + group.name
                else:
                    name = group.name

                count = get_statistics_field(name)
                set_statistics_field(name, count + 1)

    data = get_statistics()
    set_statistics_field("ФМШ", data["11 класс"] + data["10 класс"])


def reset_statistics():
    data = {
        "ФМШ":0,
        "11 класс":0,
        "10 класс":0,
        "start_count": 0,
        "timetable_count": 0,
        "settings_count": 0,
        "info_count": 0,
        "sent_notifications_count": 0,
        "error_count": 0,
    }
    school = Group(name="ФМШ")
    eleven_grade = Group(name="11 класс")
    ten_grade = Group(name="10 класс")

    for group in ten_grade.children + eleven_grade.children:
        if "группа" in group.name:
            name = group.parent.name + " " + group.name
        else:
            name = group.name

        data[name] = 0



    for key in data.keys():
        set_statistics_field(key, data[key])


if __name__ == "__main__":
    pass
    # set_statistics_field("name", "123")
