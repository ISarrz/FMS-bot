from typing import List
from dataclasses import dataclass
from modules.database_api.database.database import DB
from modules.database_api.event import Event
from typing import List
from dataclasses import dataclass
from modules.database_api.database.database import DB
from modules.database_api.group.group_patterns import group_patterns


# container structure
@dataclass
class CnGroup:
    name: str
    about: str


# database container structure
@dataclass
class DbGroup(CnGroup):
    id: int
    name: str
    about: str


class GroupDeleter:
    @staticmethod
    def delete(group: DbGroup):
        DB.delete_one(Group.table_name, id=group.id)


class GroupUpdater:
    @staticmethod
    def update_name(group: DbGroup, name: str):
        DB.update_one(Group.table_name, group.__dict__, {"name": name})

    @staticmethod
    def update_about(group: DbGroup, about: str):
        DB.update_one(Group.table_name, group.__dict__, {"about": about})


class GroupFetcher:
    @staticmethod
    def fetch_all() -> List[DbGroup]:
        return GroupFetcher.constructor(DB.fetch_many(Group.table_name))

    @staticmethod
    def fetch_by_id(id: int) -> DbGroup:
        return GroupFetcher.constructor(DB.fetch_one(Group.table_name, id=id))

    @staticmethod
    def fetch_by_name(name: str) -> DbGroup:
        name = DB.find_pattern(name, group_patterns)
        if not name:
            raise Exception(f"No group with name '{name}'")

        return GroupFetcher.constructor(DB.fetch_one(Group.table_name, name=name))

    @staticmethod
    def constructor(info) -> DbGroup | List[DbGroup] | None:
        if not info:
            return None

        if isinstance(info, list):
            return [GroupFetcher.constructor(user_info) for user_info in info]

        else:
            return DbGroup(**dict(info))


class Group:
    table_name = "groups"
    _group: DbGroup

    def __init__(self, *args, **kwargs):
        kwargs_keys = set(kwargs.keys())

        if kwargs_keys == {"id"}:
            self._group = GroupFetcher.fetch_by_id(kwargs["id"])

        elif kwargs_keys == {"name"}:
            self._group = GroupFetcher.fetch_by_name(kwargs["name"])

        else:
            raise Exception("Invalid arguments in Group fetch")

        if not self._group:
            raise Exception("Group not found")

    @staticmethod
    def all() -> DbGroup | List[DbGroup] | None:
        return GroupFetcher.fetch_all()

    @property
    def id(self) -> int:
        return self._group.id

    @property
    def name(self) -> str:
        return self._group.name

    @name.setter
    def name(self, name: str):
        GroupUpdater.update_name(self._group, name)

    @property
    def about(self) -> str:
        return self._group.about

    @about.setter
    def about(self, about: str):
        GroupUpdater.update_about(self._group, about)

    def delete(self):
        GroupDeleter.delete(self._group)


if __name__ == "__main__":
    group = Group(name="11 класс")
    print(group.about)
    group.about = 'Параллель 11 класс'
    group = Group(name="11 класс")
    print(group.about)
