from __future__ import annotations

from typing import List
from dataclasses import dataclass
from modules.database_api.database.database import DB
from typing import List
from dataclasses import dataclass
from modules.database_api.database.database import DB
from modules.database_api.event.event import Event, EventFetcher


class GroupNotFoundError(Exception):
    def __str__(self) -> str:
        return "Group not found"


class GroupAlreadyExistsError(Exception):
    def __str__(self) -> str:
        return "Group already exists"


class IncorrectGroupArgumentsError(Exception):
    def __str__(self) -> str:
        return "Incorrect group arguments"


# container structure
@dataclass
class CnGroup:
    name: str


# database container structure
@dataclass
class DbGroup(CnGroup):
    id: int
    name: str


class GroupDeleter:
    @staticmethod
    def delete(group: DbGroup):
        DB.delete_one(DB.groups_table_name, id=group.id)
        DB.delete_one(DB.users_groups_table_name, group_id=group.id)
        DB.delete_one(DB.groups_relations_table_name, parent_id=group.id)
        DB.delete_one(DB.groups_relations_table_name, child_id=group.id)

    @staticmethod
    def delete_child(parent: DbGroup, child: DbGroup):
        DB.delete_one(DB.groups_relations_table_name, parent_id=parent.id, child_id=child.id)


class GroupUpdater:
    @staticmethod
    def update_name(group: DbGroup, name: str):
        DB.update_one(DB.groups_table_name, group.__dict__, {"name": name})


class GroupFetcher:
    @staticmethod
    def fetch_all() -> List[DbGroup]:
        return GroupFetcher.constructor(DB.fetch_many(DB.groups_table_name))

    @staticmethod
    def fetch_by_id(id: int) -> DbGroup:
        return GroupFetcher.constructor(DB.fetch_one(DB.groups_table_name, id=id))

    @staticmethod
    def fetch_by_name(name: str) -> DbGroup:
        return GroupFetcher.constructor(DB.fetch_one(DB.groups_table_name, name=name))

    @staticmethod
    def constructor(info) -> DbGroup | List[DbGroup] | None:
        if not info:
            return None

        if isinstance(info, list):
            groups = [GroupFetcher.constructor(group_info) for group_info in info]

            if groups:
                return groups

            return []

        else:
            return DbGroup(**dict(info))

    @staticmethod
    def fetch_parent(child: DbGroup) -> DbGroup | None:
        parent_id = DB.fetch_one(DB.groups_relations_table_name, child_id=child.id)

        if parent_id:
            return GroupFetcher.fetch_by_id(id=parent_id["parent_id"])

        return None

    @staticmethod
    def fetch_children(parent: DbGroup) -> List[DbGroup]:
        child_ids = [child["child_id"] for child in DB.fetch_many(DB.groups_relations_table_name, parent_id=parent.id)]

        return [GroupFetcher.fetch_by_id(id) for id in child_ids]

    @staticmethod
    def fetch_child(parent: DbGroup, child: DbGroup) -> DbGroup:
        relation = DB.fetch_one(DB.groups_relations_table_name, parent_id=parent.id, child_id=child.id)

        return GroupFetcher.fetch_by_id(id=relation['child_id'])

    @staticmethod
    def fetch_relation_root(group: DbGroup) -> DbGroup:
        while GroupFetcher.fetch_parent(group):
            group = GroupFetcher.fetch_parent(group)

        return group

    @staticmethod
    def fetch_relations_path(group: DbGroup) -> List[DbGroup]:
        path = []
        while group:
            path.append(group)
            group = GroupFetcher.fetch_parent(group)

        path.reverse()

        return path

    @staticmethod
    def fetch_all_relations_roots():
        roots = []
        for group in GroupFetcher.fetch_all():
            if not GroupFetcher.fetch_parent(group):
                roots.append(group)

        return roots

    @staticmethod
    def fetch_date_events(group: DbGroup, date: str):
        return GroupFetcher.constructor(DB.fetch_many(DB.events_table_name, date=date, group_id=group.id))


class GroupInserter:
    @staticmethod
    def insert(name: str):
        DB.insert_one(DB.groups_table_name, name=name)

    @staticmethod
    def insert_child(parent: DbGroup, child: DbGroup):
        DB.insert_one(DB.groups_relations_table_name, parent_id=parent.id, child_id=child.id)


class Group:
    _group: DbGroup

    def __init__(self, *args, **kwargs):
        kwargs_keys = set(kwargs.keys())

        if kwargs_keys == {"id"}:
            self._group = GroupFetcher.fetch_by_id(kwargs.get("id"))

        elif kwargs_keys == {"name"}:
            self._group = GroupFetcher.fetch_by_name(kwargs.get("name"))

        elif kwargs_keys == {"db_group"}:
            self._group = kwargs.get("db_group")

        else:
            raise IncorrectGroupArgumentsError()

        if not self._group:
            raise GroupNotFoundError

    @property
    def parent(self) -> Group | None:
        parent = GroupFetcher.fetch_parent(self._group)

        if parent:
            return Group(db_group=parent)

        return None

    @property
    def children(self) -> List[Group]:
        return [Group(db_group=info) for info in GroupFetcher.fetch_children(self._group)]

    def delete_child(self, child: Group):
        GroupDeleter.delete_child(self._group, child._group)

    def insert_child(self, child: Group):
        GroupInserter.insert_child(self._group, child._group)

    @staticmethod
    def all() -> Group | List[Group]:
        groups = GroupFetcher.fetch_all()

        if groups:
            return [Group(db_group=info) for info in groups]

        return []

    @property
    def id(self) -> int:
        return self._group.id

    @property
    def name(self) -> str:
        return self._group.name

    @property
    def relation_root(self) -> Group | None:
        root = GroupFetcher.fetch_relation_root(self._group)

        if root:
            return Group(db_group=root)

        return None

    @property
    def relation_path(self) -> List[Group]:
        path = GroupFetcher.fetch_relations_path(self._group)

        if path:
            return [Group(db_group=info) for info in path]

        return []

    @property
    def relation_height(self):
        return len(self.relation_path) - 1

    @staticmethod
    def all_relations_roots():
        return [Group(db_group=info) for info in GroupFetcher.fetch_all_relations_roots()]

    @name.setter
    def name(self, name: str):
        GroupUpdater.update_name(self._group, name)
        self._group.name = name

    @staticmethod
    def insert(name: str):
        try:
            Group(name=name)

            raise GroupAlreadyExistsError

        except GroupNotFoundError:
            GroupInserter.insert(name)

            return Group(name=name)

    def get_date_events(self, date: str):
        events = GroupFetcher.fetch_date_events(self._group, date)
        if events:
            return [Event(db_event=event_info) for event_info in events]

        return None

    def delete(self):
        GroupDeleter.delete(self._group)

    def __str__(self):
        return f"Group id: {self.id}, name: {self.name}"


if __name__ == "__main__":
    pass
