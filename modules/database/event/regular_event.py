from typing import List
from dataclasses import dataclass
from datetime import datetime
from modules.database.database.database import DB
from modules.database.group.group import Group
from modules.database.event.event import Event
from modules.time.dates import get_current_string_dates


class InvalidRegularEventArgumentsError(Exception):
    def __str__(self):
        return "Invalid regular event arguments"


class RegularEventNotFoundError(Exception):
    def __str__(self):
        return "Regular event not found"


class RegularEventAlreadyExistsError(Exception):
    def __str__(self):
        return "Regular event already exists"


@dataclass
class DbRegularEvent:
    id: int
    name: str
    group_id: int
    weekday: str
    start: str
    end: str
    owner: str
    place: str


class RegularEventDeleter:
    @staticmethod
    def delete(regular_event: DbRegularEvent):
        DB.delete_one(DB.regular_events_table_name, id=regular_event.id)


class RegularEventUpdater:
    @staticmethod
    def update_name(regular_event: DbRegularEvent, name: str):
        DB.update_one(DB.regular_events_table_name, dict(id=regular_event.id), {"name": name})

    @staticmethod
    def update_group_id(regular_event: DbRegularEvent, group_id: int):
        DB.update_one(DB.regular_events_table_name, dict(id=regular_event.id), {"group_id": group_id})

    @staticmethod
    def update_weekday(regular_event: DbRegularEvent, weekday: str):
        DB.update_one(DB.regular_events_table_name, dict(id=regular_event.id), {"weekday": weekday})

    @staticmethod
    def update_start(regular_event: DbRegularEvent, start: str):
        DB.update_one(DB.regular_events_table_name, dict(id=regular_event.id), {"start": start})

    @staticmethod
    def update_end(regular_event: DbRegularEvent, end: str):
        DB.update_one(DB.regular_events_table_name, dict(id=regular_event.id), {"end": end})

    @staticmethod
    def update_owner(regular_event: DbRegularEvent, owner: str):
        DB.update_one(DB.regular_events_table_name, dict(id=regular_event.id), {"owner": owner})

    @staticmethod
    def update_place(regular_event: DbRegularEvent, place: str):
        DB.update_one(DB.regular_events_table_name, dict(id=regular_event.id), {"place": place})


class RegularEventFetcher:
    @staticmethod
    def fetch_by_id(id: int):
        return RegularEventFetcher.constructor(DB.fetch_one(DB.regular_events_table_name, id=id))

    @staticmethod
    def fetch(**kwargs):
        return RegularEventFetcher.constructor(DB.fetch_one(DB.regular_events_table_name, **kwargs))

    @staticmethod
    def fetch_all() -> List[DbRegularEvent]:
        return RegularEventFetcher.constructor(DB.fetch_many(DB.regular_events_table_name))

    @staticmethod
    def constructor(info):
        if not info:
            return None

        if isinstance(info, list):
            events = [RegularEventFetcher.constructor(event_info) for event_info in info]
            if events:
                return events

            return []

        else:
            return DbRegularEvent(
                id=info["id"],
                name=info["name"],
                group_id=info["group_id"],
                weekday=info["weekday"],
                start=info["start"],
                end=info["end"],
                owner=info["owner"],
                place=info["place"]
            )


class RegularEventInserter:
    @staticmethod
    def insert(name: str, group_id: int, weekday: str, start: str, end: str, owner: str, place: str):
        return DB.insert_one(DB.regular_events_table_name,
                             name=name,
                             group_id=group_id,
                             weekday=weekday,
                             start=start,
                             end=end,
                             owner=owner,
                             place=place)


class RegularEvent:
    _regular_event: DbRegularEvent
    _generated_events: List[Event]

    def __init__(self, *args, **kwargs):

        fields = ["id", "name", "group_id", "weekday", "start", "end", "owner", "place", "db_event"]

        for field in kwargs.keys():
            if field not in fields:
                raise InvalidRegularEventArgumentsError

        if "db_regular_event" in kwargs.keys():
            self._regular_event = kwargs["db_regular_event"]

        elif "id" in kwargs.keys():
            self._regular_event = RegularEventFetcher.fetch_by_id(id=kwargs["id"])

        else:
            self._regular_event = RegularEventFetcher.fetch(**kwargs)

        if not self._regular_event:
            raise RegularEventNotFoundError

    def add_events(self):
        for date in get_current_string_dates():
            dt = datetime.strptime(date, "%d-%m-%Y")
            weekday = dt.weekday()
            if weekday != self.weekday:
                continue

            event = Event.insert(name=self.name,
                                 group_id=self.group_id,
                                 date=date,
                                 start=self.start,
                                 end=self.end,
                                 owner=self.owner,
                                 place=self.place)

            self._generated_events.append(event)

    @staticmethod
    def all():
        regular_events = RegularEventFetcher.fetch_all()
        if regular_events:
            return [RegularEvent(db_event=event_info) for event_info in regular_events]

        return []

    @property
    def name(self) -> str:
        return self._regular_event.name

    @name.setter
    def name(self, name: str):
        RegularEventUpdater.update_name(self._regular_event, name)
        self._regular_event.name = name

    @property
    def id(self):
        return self._regular_event.id

    @property
    def group_id(self) -> int:
        return self._regular_event.group_id

    @property
    def group(self):
        return Group(id=self._regular_event.group_id)

    @group.setter
    def group(self, group: Group):
        RegularEventUpdater.update_group_id(self._regular_event, group.id)
        self._regular_event.group = group
        self._regular_event._group_id = group.id

    @group_id.setter
    def group_id(self, group_id: int):
        RegularEventUpdater.update_group_id(self._regular_event, group_id)
        self._regular_event.group_id = group_id

    @property
    def weekday(self) -> str:
        return self._regular_event.weekday

    @weekday.setter
    def weekday(self, weekday: str):
        RegularEventUpdater.update_weekday(self._regular_event, weekday)
        self._regular_event.weekday = weekday

    @property
    def start(self) -> str:
        return self._regular_event.start

    @start.setter
    def start(self, start: str):
        RegularEventUpdater.update_start(self._regular_event, start)
        self._regular_event.start = start

    @property
    def end(self) -> str:
        return self._regular_event.end

    @end.setter
    def end(self, end: str):
        RegularEventUpdater.update_end(self._regular_event, end)
        self._regular_event.end = end

    @property
    def owner(self) -> str:
        return self._regular_event.owner

    @owner.setter
    def owner(self, owner: str):
        RegularEventUpdater.update_owner(self._regular_event, owner)
        self._regular_event.owner = owner

    @property
    def place(self) -> str:
        return self._regular_event.place

    @place.setter
    def place(self, place: str):
        RegularEventUpdater.update_place(self._regular_event, place)
        self._regular_event.place = place

    def delete(self):
        RegularEventDeleter.delete(self._regular_event)

        for event in self._generated_events:
            event.delete()

    @staticmethod
    def insert(name: str, group_id: int, weekday: str, start: str, end: str, owner: str, place: str):
        try:
            RegularEvent(name=name, group_id=group_id, weekday=weekday, start=start, end=end, owner=owner, place=place)
            raise RegularEventAlreadyExistsError

        except RegularEventNotFoundError:
            event_id = RegularEventInserter.insert(name=name, group_id=group_id, weekday=weekday, start=start, end=end,
                                                   owner=owner,
                                                   place=place)

            return RegularEvent(id=event_id)
