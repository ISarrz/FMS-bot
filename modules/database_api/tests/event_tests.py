import pytest
from modules.database_api.group.group import Group
from modules.database_api.event.event import Event


@pytest.fixture(autouse=True)
def clear_database():
    for event in Event.all():
        event.delete()
    for group in Group.all():
        group.delete()


def test_insert():
    group = Group.insert("11 класс")
    event1 = Event.insert("урок", group.id, "07.09.2025", "8:30", "9:15", "учитель", "кабинет")
    event2 = Event(group_id=event1.group.id, name=event1.name)

    assert event1.group_id == event2.group.id

    assert event1.id == event2.id


def test_update():
    group = Group.insert("11 класс")
    event = Event.insert("урок", group.id, "07.09.2025", "8:30", "9:15", "учитель", "кабинет")

    group2 = Group.insert("10 класс")
    event.name = "1"
    event.group_id = 1
    event.date = "1"
    event.start = "1"
    event.end = "1"
    event.owner = "1"
    event.place = "1"
    event.group = group

    assert event.name == "1"
    assert event.group_id == 1
    assert event.date == "1"
    assert event.start == "1"
    assert event.end == "1"
    assert event.owner == "1"
    assert event.place == "1"


def test_multiple_fetch():
    group = Group.insert("11 класс")
    date = "07.09.2025"
    event1 = Event.insert("урок 2", group.id, date, "9:30", "10:15", "учитель", "кабинет")
    event2 = Event.insert("урок 1", group.id, date, "8:30", "9:15", "учитель", "кабинет")
    event3 = Event.insert("урок 2", group.id, date, "8:30", "9:20", "учитель", "кабинет")

    events = Event.by_group_and_date(group, date)
    assert events[0].id == event2.id
    assert events[1].id == event3.id
    assert events[2].id == event1.id
