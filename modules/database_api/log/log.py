from __future__ import annotations

from typing import List
from dataclasses import dataclass
from modules.database_api.database.database import DB
from typing import List
from dataclasses import dataclass
from modules.database_api.database.database import DB
from modules.database_api.event.event import EventFetcher
from modules.database_api.group.group_patterns import group_patterns
from modules.database_api.user.user import UserFetcher


class InvalidLogArgumentError(Exception):
    def __str__(self) -> str:
        return "Invalid log argument"


class LogNotFoundError(Exception):
    def __str__(self) -> str:
        return "Log not found"


@dataclass
class DbLog:
    id: int
    value: str


class LogFetcher:
    @staticmethod
    def fetch_all() -> List[DbLog]:
        return LogFetcher.constructor(DB.fetch_many(DB.logs_table_name))

    @staticmethod
    def fetch_by_id(id: int) -> DbLog:
        return LogFetcher.constructor(DB.fetch_one(DB.logs_table_name, id=id))

    @staticmethod
    def constructor(info):
        if not info:
            return None

        if isinstance(info, list):
            return [LogFetcher.constructor(log_info) for log_info in info]

        else:
            return DbLog(id=info["id"], value=info["value"])


class LogInserter:
    @staticmethod
    def insert(value: str):
        DB.insert_one(DB.logs_table_name, value=value)


class LogDeleter:
    @staticmethod
    def delete(log: DbLog):
        DB.delete_one(DB.logs_table_name, id=log.id)


class Log:
    _log: DbLog

    def __init__(self, **kwargs):
        if "id" in kwargs.keys():
            self._log = LogFetcher.fetch_by_id(kwargs["id"])

        elif "db_log" in kwargs.keys():
            self._log = kwargs["db_log"]

        else:
            raise InvalidLogArgumentError

        if not self._log:
            raise LogNotFoundError

    @staticmethod
    def insert(value: str):
        LogInserter.insert(value)

    def delete(self):
        LogDeleter.delete(self._log)

    @staticmethod
    def all() -> List[Log]:
        logs = LogFetcher.fetch_all()

        if logs:
            return [Log(db_log=log) for log in logs]

        return []
