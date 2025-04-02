from typing import List
from dataclasses import dataclass
from modules.database_api.database.database import DB


@dataclass
class CnUser:
    telegram_id: int


@dataclass
class DbUser(CnUser):
    id: int
    telegram_id: int


class UserDeleter:
    pass


class UserUpdater:
    pass


class UserFetcher:
    def __call__(self, *args, **kwargs):
        kwargs_keys = set(kwargs.keys())

        if kwargs_keys == {"id"}:
            self._fetch_by_id(kwargs["id"])

        elif kwargs_keys == {"telegram_id"}:
            self._fetch_by_telegram_id(kwargs["telegram_id"])

        elif kwargs.get('all', False):
            self._fetch_all()

        raise "Invalid arguments in User fetch"

    def all(self) -> List[DbUser]:
        return self._fetch_all()

    @staticmethod
    def _fetch_by_id(id) -> DbUser:
        return User.constructor(DB.fetch_one(User.table_name, id=id))

    @staticmethod
    def _fetch_by_telegram_id(telegram_id: int) -> DbUser:
        return User.constructor(DB.fetch_one(User.table_name, telegram_id=telegram_id))

    @staticmethod
    def _fetch_all() -> List[DbUser]:
        return User.constructor(DB.fetch_all(User.table_name))


class User:
    table_name = "users"
    fetch = UserFetcher()
    delete = UserDeleter()
    update = UserUpdater()

    @staticmethod
    def constructor(info):
        if not info:
            return None

        if isinstance(info, list):
            return [User.constructor(user_info) for user_info in info]

        else:
            return DbUser(id=info['id'], telegram_id=info['telegram_id'])
