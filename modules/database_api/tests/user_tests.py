from modules.database_api.user.user import User, UserNotFoundError, UserAlreadyExistsError, InvalidUserArgumentsError
import pytest


@pytest.fixture(autouse=True)
def clear_database():
    for user in User.all():
        user.delete()


def test_insert():
    User.insert(telegram_id=1)
    user = User(telegram_id=1)
    print(user.id)
    print(user.telegram_id)
    user.delete()


def test_get():
    try:
        user = User(telegram_id=-1)
        print(user.id)
    except UserNotFoundError:
        print("User not found")


def test_insert_existing_user():
    try:
        User.insert(telegram_id=1)
        user = User(telegram_id=1)
        print(user.id)
        print(user.telegram_id)
        User.insert(telegram_id=1)

    except UserAlreadyExistsError:
        print("User already exists")


def test_invalid_argument():
    try:
        user = User(name=1)
    except InvalidUserArgumentsError:
        print("Invalid user arguments")


def test_all():
    user1 = User.insert(telegram_id=1)
    user2 = User.insert(telegram_id=2)
    user3 = User.insert(telegram_id=3)
    users = User.all()
    for user in users:
        print(user)


def test_user_notifications():
    user = User.insert(telegram_id=1)
    print(user.notifications)
    user.notifications = False
    print(user.notifications)
