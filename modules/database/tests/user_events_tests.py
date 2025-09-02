import pytest
from modules.database.user.user import User
from modules.database.event.event import Event
from modules.database.group.group import Group


@pytest.fixture(autouse=True)
def clear_database():
    for user in User.all():
        user.delete()

    for group in Group.all():
        group.delete()

    for event in Event.all():
        event.delete()


def test_insert_user_group():
    user = User.insert(telegram_id=1)
    group1 = Group.insert(name='group 1')
    group2 = Group.insert(name='group 2')

    user.insert_group(group1)
    user.insert_group(group2)

    date = "07.09.2025"

    event1 = Event.insert("урок 1", group1.id, date, "0:1", "9:15", "учитель", "кабинет")
    event2 = Event.insert("урок 2", group1.id, date, "0:2", "9:15", "учитель", "кабинет")
    event3 = Event.insert("урок 3", group2.id, date, "0:3", "9:15", "учитель", "кабинет")
    event4 = Event.insert("урок 4", group2.id, date, "0:4", "9:15", "учитель", "кабинет")

    user_events = user.date_events(date=date)
    assert user_events[0].id == event1.id
    assert user_events[1].id == event2.id
    assert user_events[2].id == event3.id
    assert user_events[3].id == event4.id

