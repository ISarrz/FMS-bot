from typing import List
from dataclasses import dataclass
from modules.database_api.database.database import DB


@dataclass
class CnEvent:
    name: str
    about: str
    date: str
    start: str
    end: str
    owner: str
    place: str


@dataclass
class DbEvent(CnEvent):
    id: int
    name: str
    about: str
    date: str
    start: str
    end: str
    owner: str
    place: str


class EventDeleter:
    pass


class EventUpdater:
    pass


class EventFetcher:
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

    def all(self) -> List[DbEvent]:
        return self._fetch_all()

    @staticmethod
    def _fetch_by_id(id) -> DbEvent:
        return Event.constructor(DB.fetch_one(Event.table_name, id=id))

    @staticmethod
    def _fetch_by_name(name: str) -> DbEvent:
        return Event.constructor(DB.fetch_one(Event.table_name, name=name))

    @staticmethod
    def _fetch_by_about(about: str) -> DbEvent:
        return Event.constructor(DB.fetch_one(Event.table_name, about=about))

    @staticmethod
    def _fetch_all() -> List[DbEvent]:
        return Event.constructor(DB.fetch_all(Event.table_name))


class Event:
    table_name = "events"
    # event = GroupEvent()
    fetch = EventFetcher()
    delete = EventDeleter()
    update = EventUpdater()

    @staticmethod
    def constructor(info):
        if not info:
            return None

        if isinstance(info, list):
            return [Event.constructor(event_info) for event_info in info]

        else:
            return DbEvent(
                id=info['id'],
                name=info['first_name'],
                about=info['last_name'],
            )
