from __future__ import annotations

from dataclasses import dataclass
from modules.database.database.database import DB


class TimetableNotFoundError(Exception):
    def __str__(self) -> str:
        return "Image not found"


class IncorrectTimetableArgumentsError(Exception):
    def __str__(self) -> str:
        return "Incorrect image arguments"


@dataclass
class DbTimetable:
    id: int
    user_id: int
    date: str
    image: bytes
    text: str


class TimetableFetcher:
    @staticmethod
    def fetch_all():
        return TimetableFetcher.constructor(DB.fetch_many(DB.timetable_table_name))

    @staticmethod
    def fetch_by_id(id: int):
        return TimetableFetcher.constructor(DB.fetch_many(DB.timetable_table_name, id=id))

    @staticmethod
    def fetch_by_user_id_and_date(user_id: int, date: str):
        return TimetableFetcher.constructor(DB.fetch_many(DB.timetable_table_name, user_id=user_id, date=date))

    @staticmethod
    def fetch(**kwargs):
        return TimetableFetcher.constructor(DB.fetch_one(DB.timetable_table_name, **kwargs))

    @staticmethod
    def fetch_by_user_id(user_id: int):
        return TimetableFetcher.constructor(DB.fetch_many(DB.timetable_table_name, user_id=user_id))

    @staticmethod
    def constructor(info):
        if not info:
            return None

        if isinstance(info, list):
            return [TimetableFetcher.constructor(timetable_info) for timetable_info in info]

        else:
            return DbTimetable(**dict(info))


class ImageDeleter:
    @staticmethod
    def delete(timetable: DbTimetable):
        DB.delete_one(DB.timetable_table_name, id=timetable.id)


class ImageInserter:
    @staticmethod
    def insert(user_id: int, date: str, image: bytes, text: str):
        DB.insert_one(DB.timetable_table_name, user_id=user_id, date=date, image=image, text=text)


class Timetable:
    _timetable: DbTimetable

    def __init__(self, *args, **kwargs):
        kwargs_keys = set(kwargs.keys())

        fields = ["id", "user_id", "date", "image", "db_timetable", "text"]
        for field in kwargs.keys():
            if field not in fields:
                raise IncorrectTimetableArgumentsError

        if kwargs_keys == {"id"}:
            self._timetable = TimetableFetcher.fetch_by_id(kwargs.get("id"))

        elif kwargs_keys == {"db_timetable"}:
            self._timetable = kwargs.get("db_timetable")

        else:
            self._timetable = TimetableFetcher.fetch(**kwargs)

        if not self._timetable:
            raise TimetableNotFoundError

    @staticmethod
    def all():
        timetable = TimetableFetcher.fetch_all()
        if timetable:
            return [Timetable(db_timetable=timetable_info) for timetable_info in timetable]

        return []

    @property
    def id(self) -> int:
        return self._timetable.id

    @property
    def date(self) -> str:
        return self._timetable.date

    @property
    def image(self) -> bytes:
        return self._timetable.image

    @property
    def text(self) -> str:
        return self._timetable.text

    @staticmethod
    def exist(**kwargs):
        try:
            Timetable(**kwargs)
            return True

        except TimetableNotFoundError:
            return False

    @staticmethod
    def insert(user_id: int, date: str, image: bytes, text: str):
        try:
            Timetable(user_id=user_id, date=date, image=image, text=text)

        except TimetableNotFoundError:
            pass
            ImageInserter.insert(user_id, date, image, text)
            return Timetable(user_id=user_id, date=date, image=image, text=text)

    @staticmethod
    def by_user_id_and_date(user_id: int, date: str):
        timetable = TimetableFetcher.fetch_by_user_id_and_date(user_id, date)
        if timetable:
            return [Timetable(db_timetable=timetable_info) for timetable_info in timetable]

        return []

    @staticmethod
    def user_timetable(user_id: int):
        timetable = TimetableFetcher.fetch_by_user_id(user_id)
        if timetable:
            return [Timetable(db_timetable=timetable_info) for timetable_info in timetable]

        return []

    def delete(self):
        ImageDeleter.delete(self._timetable)
