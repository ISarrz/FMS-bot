import pytest
from modules.database.user.user import User, UserNotFoundError, UserAlreadyExistsError, InvalidUserArgumentsError


@pytest.fixture(autouse=True)
def clear_database():
    for user in User.all():
        user.delete()


def test_insert():
    user1 = User.insert(telegram_id=1)
    user2 = User(telegram_id=1)

    assert user1.telegram_id == 1
    assert user2.telegram_id == 1
    assert user1.id == user2.id


def test_get():
    try:
        user = User(telegram_id=-1)
        print(user.id)
    except UserNotFoundError:
        print("\nUser not found")


def test_insert_existing_user():
    try:
        User.insert(telegram_id=1)
        user = User(telegram_id=1)
        print(user.id)
        print(user.telegram_id)
        User.insert(telegram_id=1)

    except UserAlreadyExistsError:
        print("\nUser already exists")


def test_invalid_argument():
    try:
        user = User(name=1)
    except InvalidUserArgumentsError:
        print("\nInvalid user arguments")


def test_all():
    user1 = User.insert(telegram_id=1)
    user2 = User.insert(telegram_id=2)
    user3 = User.insert(telegram_id=3)
    users = User.all()
    print()
    for user in users:
        print(user)


def test_user_notifications():
    user = User.insert(telegram_id=1)
    print()
    print(user.settings.notifications)
    user.settings.notifications = False
    print(user.settings.notifications)

    user.notifications = ["Hello World"]
    notifications = user.notifications
    for notification in notifications:
        print(notification.value)
        notification.delete()

    print(user.notifications)
