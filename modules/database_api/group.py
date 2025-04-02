from typing import List
from dataclasses import dataclass
from modules.database_api.database.database import DB
from modules.database_api.event import Event

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
    pass


class GroupUpdater:
    pass


class GroupFetcher:
    def __call__(self, *args, **kwargs):
        kwargs_keys = set(kwargs.keys())

        if kwargs_keys == {"id"}:
            self._fetch_by_id(kwargs["id"])

        elif kwargs_keys == {"name"}:
            self._fetch_by_name(kwargs["name"])

        elif kwargs_keys == {"about"}:
            self._fetch_by_about(kwargs["about"])

        elif kwargs.get('all', False):
            self._fetch_all()

        raise "Invalid arguments in Group fetch"

    def all(self) -> List[DbGroup]:
        return self._fetch_all()

    @staticmethod
    def _fetch_by_id(id) -> DbGroup:
        return Group.constructor(DB.fetch_one(Group.table_name, id=id))

    @staticmethod
    def _fetch_by_name(name: str) -> DbGroup:
        return Group.constructor(DB.fetch_one(Group.table_name, name=name))

    @staticmethod
    def _fetch_by_about(about: str) -> DbGroup:
        return Group.constructor(DB.fetch_one(Group.table_name, about=about))

    @staticmethod
    def _fetch_all() -> List[DbGroup]:
        return Group.constructor(DB.fetch_all(Group.table_name))


class GroupEvent:
    pass

    def __call__(self, *args, **kwargs):
        pass

    def all(self) -> List[DbGroup]:


class Group:
    table_name = "groups"
    event = GroupEvent()
    fetch = GroupFetcher()
    delete = GroupDeleter()
    update = GroupUpdater()

    @staticmethod
    def constructor(info):
        if not info:
            return None

        if isinstance(info, list):
            return [Group.constructor(group_info) for group_info in info]

        else:
            return DbGroup(
                id=info['id'],
                name=info['first_name'],
                about=info['last_name'],
            )
