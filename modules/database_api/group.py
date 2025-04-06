from typing import List
from dataclasses import dataclass
from modules.database_api.database.database import DB
from modules.database_api.event import Event
from typing import List
from dataclasses import dataclass
from modules.database_api.database.database import DB


@dataclass
class CnGroup:
    name: str
    about: str


@dataclass
class DbGroup(CnGroup):
    id: int
    name: str
    about: str




class GroupDeleter:
    @staticmethod
    def delete(group):
        DB.delete_one(Group.table_name, id=group.id)


class GroupFetcher:
    @staticmethod
    def fetch_all() -> List[Group]:
        return UserFetcher.constructor(DB.fetch_many(User.table_name))

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


class User:
    table_name = "users"
    user: DbUser

    def __init__(self, *args, **kwargs):
        kwargs_keys = set(kwargs.keys())

        if kwargs_keys == {"id"}:
            self.user = UserFetcher.fetch_by_id(kwargs["id"])

        elif kwargs_keys == {"telegram_id"}:
            self.user = UserFetcher.fetch_by_telegram_id(kwargs["telegram_id"])

        raise "Invalid arguments in User fetch"

    @staticmethod
    def all():
        return UserFetcher.fetch_all()

    @property
    def id(self) -> int:
        return self.user.id

    @property
    def telegram_id(self) -> int:
        return self.user.telegram_id

    def __del__(self):
        UserDeleter.delete(self.user)
