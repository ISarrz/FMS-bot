from typing import List
from dataclasses import dataclass
from modules.database_api.database.database import DB
from modules.database_api.group.group import Group


@dataclass
class CnUser:
    telegram_id: int


@dataclass
class DbUser(CnUser):
    id: int
    telegram_id: int


class UserFetcher:
    users_groups_table = 'users_groups'

    @staticmethod
    def fetch_all() -> List[DbUser]:
        return UserFetcher.constructor(DB.fetch_many(User.table_name))

    @staticmethod
    def fetch_groups(user: DbUser) -> List[Group]:
        user_groups = DB.fetch_many(UserFetcher.users_groups_table, user_id=user.id)

    @staticmethod
    def fetch_by_telegram_id(telegram_id: int):
        return UserFetcher.constructor(DB.fetch_one(User.table_name, telegram_id=telegram_id))

    @staticmethod
    def fetch_by_id(id: int) -> DbUser:
        return UserFetcher.constructor(DB.fetch_one(User.table_name, id=id))

    @staticmethod
    def constructor(info) -> DbUser | List[DbUser] | None:
        if not info:
            return None

        if isinstance(info, list):
            return [UserFetcher.constructor(user_info) for user_info in info]

        else:
            return DbUser(id=info['id'], telegram_id=info['telegram_id'])


class UserDeleter:
    @staticmethod
    def delete(user):
        DB.delete_one(User.table_name, id=user.id)


class User:
    table_name = "users"
    users_groups_table_name = "users_groups"

    _user: DbUser

    def __init__(self, *args, **kwargs):
        kwargs_keys = set(kwargs.keys())

        if kwargs_keys == {"id"}:
            self._user = UserFetcher.fetch_by_id(kwargs["id"])

        elif kwargs_keys == {"telegram_id"}:
            self._user = UserFetcher.fetch_by_telegram_id(kwargs["telegram_id"])

        elif kwargs_keys == {"db_user"}:
            self._user = kwargs["db_user"]

        else:
            raise "Invalid arguments in User fetch"

    @staticmethod
    def all():
        return UserFetcher.fetch_all()

    @property
    def id(self) -> int:
        return self._user.id

    @property
    def telegram_id(self) -> int:
        return self._user.telegram_id

    @property
    def groups(self) -> List[Group]:
        return UserFetcher.fetch_groups(self._user)

    def delete(self):
        UserDeleter.delete(self._user)
