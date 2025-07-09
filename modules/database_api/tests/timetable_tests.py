from modules.database_api.timetable.timetable import Timetable
from modules.database_api.user.user import User
import pytest
from PIL import Image


@pytest.fixture(autouse=True)
def clear_database():
    for user in User.all():
        user.delete()
    for timetable in Timetable.all():
        timetable.delete()


def test_timetable_creation():
    image = open("/home/zero/PycharmProjects/FMS-bot/modules/database_api/tests/img.png", "rb").read()
    user = User.insert(telegram_id=1)
    date = "07.08.2025"
    timetable = Timetable.insert(user_id=user.id, date=date, image=image)
    assert Timetable.all()[0].image == image

