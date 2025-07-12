import pytest
from modules.database.timetable.timetable import Timetable
from modules.database.user.user import User



@pytest.fixture(autouse=True)
def clear_database():
    for user in User.all():
        user.delete()
    for timetable in Timetable.all():
        timetable.delete()


def test_timetable_creation():
    image = open("/home/zero/PycharmProjects/FMS-bot/modules/database/tests/img.png", "rb").read()
    user = User.insert(telegram_id=1)
    date = "07.08.2025"
    timetable = Timetable.insert(user_id=user.id, date=date, image=image)
    assert Timetable.all()[0].image == image

