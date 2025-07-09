from modules.database_api.user.user import User
from modules.database_api.event.event import Event
from modules.database_api.group.group import Group
from modules.database_api.timetable.timetable import Timetable
import pytest


@pytest.fixture(autouse=True)
def clear_database():
    for user in User.all():
        user.delete()

    for event in Event.all():
        event.delete()

    for timetable in Timetable.all():
        timetable.delete()

    for group in Group.all():
        group.delete()

def test_core_functionality():
    user = User.insert(1)
    date = "07.08.2025"
    group = Group.insert(name="11 класс")
    user.insert_group(group)
    event = Event.insert("урок", group.id, date, "8:30", "9:15", "учитель", "кабинет")

    image = open("/home/zero/PycharmProjects/FMS-bot/modules/database_api/tests/img.png", "rb").read()

    timetable = user.insert_timetable(date=date, image=image)

    event.delete()


    assert Timetable.all() == []

def test_user_timetable():
    user = User.insert(1)
    date = "07.08.2025"
    group = Group.insert(name="11 класс")
    user.insert_group(group)
    event = Event.insert("урок", group.id, date, "8:30", "9:15", "учитель", "кабинет")

    image = open("/home/zero/PycharmProjects/FMS-bot/modules/database_api/tests/img.png", "rb").read()

    timetable = user.insert_timetable(date=date, image=image)

    assert user.get_date_timetable(date=date).id == Timetable.all()[0].id