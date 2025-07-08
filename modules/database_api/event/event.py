from typing import List
from dataclasses import dataclass

from seobject import kwargs

from modules.database_api.database.database import DB

from modules.database_api.group.group import Group


class InvalidEventArgumentsError(Exception):
    def __str__(self):
        return "Invalid event arguments"


class EventNotFoundError(Exception):
    def __str__(self):
        return "Event not found"


class EventAlreadyExistsError(Exception):
    def __str__(self):
        return "Event already exists"


@dataclass
class CnEvent:
    name: str
    group_id: int
    date: str
    start: str
    end: str
    owner: str
    place: str


@dataclass
class DbEvent(CnEvent):
    id: int
    name: str
    group_id: int
    date: str
    start: str
    end: str
    owner: str
    place: str


class EventDeleter:
    @staticmethod
    def delete(event: DbEvent):
        DB.delete_one(DB.events_table_name, id=event.id)


class EventUpdater:
    @staticmethod
    def update_name(event: DbEvent, name: str):
        DB.update_one(DB.events_table_name, dict(id=event.id), {"name": name})

    @staticmethod
    def update_group_id(event: DbEvent, group_id: int):
        DB.update_one(DB.events_table_name, dict(id=event.id), {"group_id": group_id})

    @staticmethod
    def update_date(event: DbEvent, date: str):
        DB.update_one(DB.events_table_name, dict(id=event.id), {"date": date})

    @staticmethod
    def update_start(event: DbEvent, start: str):
        DB.update_one(DB.events_table_name, dict(id=event.id), {"start": start})

    @staticmethod
    def update_end(event: DbEvent, end: str):
        DB.update_one(DB.events_table_name, dict(id=event.id), {"end": end})

    @staticmethod
    def update_owner(event: DbEvent, owner: str):
        DB.update_one(DB.events_table_name, dict(id=event.id), {"owner": owner})

    @staticmethod
    def update_place(event: DbEvent, place: str):
        DB.update_one(DB.events_table_name, dict(id=event.id), {"place": place})


class EventFetcher:
    @staticmethod
    def fetch_event(**kwargs):
        return EventFetcher.constructor(DB.fetch_one(DB.events_table_name, **kwargs))

    @staticmethod
    def fetch_all() -> List[DbEvent]:
        return EventFetcher.constructor(DB.fetch_many(DB.events_table_name))

    @staticmethod
    def constructor(info):
        if not info:
            return None

        if isinstance(info, list):
            events = [EventFetcher.constructor(event_info) for event_info in info]
            if events:
                return events

            return []

        else:
            return DbEvent(
                id=info["id"],
                name=info["name"],
                group_id=info["group_id"],
                date=info["date"],
                start=info["start"],
                end=info["end"],
                owner=info["owner"],
                place=info["place"]
            )


class EventInserter:
    @staticmethod
    def insert(event: DbEvent):
        DB.insert_one(DB.events_table_name,
                      name=event.name,
                      group_id=event.group_id,
                      date=event.date,
                      start=event.start,
                      end=event.end,
                      owner=event.owner,
                      place=event.place)


class Event:
    _event: DbEvent

    def __init__(self, *args, **kwargs):
        kwargs_keys = set(kwargs.keys())

        fields = ["id", "name", "group_id", "date", "start", "end", "owner", "place"]

        for field in kwargs.keys():
            if field not in fields:
                raise InvalidEventArgumentsError

        if kwargs_keys == {"db_event"}:
            self._event = kwargs["db_event"]

        else:
            self._event = EventFetcher.fetch_event(**kwargs)

        if not self._event:
            raise EventNotFoundError

    @property
    def name(self) -> str:
        return self._event.name

    @name.setter
    def name(self, name: str):
        EventUpdater.update_name(self._event, name)
        self._event.name = name

    @property
    def id(self):
        return self._event.id

    @property
    def group_id(self) -> int:
        return self._event.group_id

    @property
    def group(self):
        return Group(self._event.group_id)

    @group_id.setter
    def group_id(self, group: Group):
        EventUpdater.update_group_id(self._event, group.id)
        self._event.group_id = group.id

    @property
    def date(self) -> str:
        return self._event.date

    @date.setter
    def date(self, date: str):
        EventUpdater.update_date(self._event, date)
        self._event.date = date

    @property
    def start(self) -> str:
        return self._event.start

    @start.setter
    def start(self, start: str):
        EventUpdater.update_start(self._event, start)
        self._event.start = start

    @property
    def end(self) -> str:
        return self._event.end

    @end.setter
    def end(self, end: str):
        EventUpdater.update_end(self._event, end)
        self._event.end = end

    @property
    def owner(self) -> str:
        return self._event.owner

    @owner.setter
    def owner(self, owner: str):
        EventUpdater.update_owner(self._event, owner)
        self._event.owner = owner

    @property
    def place(self) -> str:
        return self._event.place

    @place.setter
    def place(self, place: str):
        EventUpdater.update_place(self._event, place)
        self._event.place = place

    def delete(self):
        EventDeleter.delete(self._event)

    @staticmethod
    def insert(event: DbEvent):
        try:
            Event(db_event=event)
            raise EventAlreadyExistsError

        except EventNotFoundError:
            EventInserter.insert(event)
