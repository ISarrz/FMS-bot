import pytest
from modules.database.user.user import User
from modules.database.group.group import Group


@pytest.fixture(autouse=True)
def clear_database():
    for user in User.all():
        user.delete()

    for group in Group.all():
        group.delete()


def test_insert_user_group():
    user = User.insert(telegram_id=1)
    group1 = Group.insert(name='group 1')
    group2 = Group.insert(name='group 2')

    user.insert_group(group1)
    user.insert_group(group2)

    print()
    for group in user.groups:
        print(group)

    user.delete_group(group1)
    print('deleted group 1')
    for group in user.groups:
        print(group)
