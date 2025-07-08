from __future__ import annotations

from typing import List
from dataclasses import dataclass

from modules.database_api.database.database import DB
from modules.database_api.group.group import Group, DbGroup
from modules.database_api.user.user_settings import UserSettings, UserSettingsUpdater
from modules.database_api.event.event import Event, DbEvent, EventFetcher
from modules.database_api.user.user_notification import UserNotification


class UserNotFoundError(Exception):
    def __str__(self) -> str:
        return "User not found"


class UserAlreadyExistsError(Exception):
    def __str__(self) -> str:
        return "User not found"


class InvalidUserArgumentsError(Exception):
    def __str__(self) -> str:
        return "Invalid user arguments"


@dataclass
class CnUser:
    telegram_id: int


@dataclass
class DbUser(CnUser):
    id: int
    telegram_id: int


class UserFetcher:
    @staticmethod
    def fetch_all() -> List[DbUser]:
        return UserFetcher.constructor(DB.fetch_many(DB.users_table_name))

    @staticmethod
    def fetch_groups(user: DbUser) -> List[Group]:
        user_groups_ids = [info["group_id"] for info in DB.fetch_many(DB.users_groups_table_name, user_id=user.id)]

        if user_groups_ids:
            return [Group(id=group_id) for group_id in user_groups_ids]

        return []

    @staticmethod
    def fetch_by_telegram_id(telegram_id: int):
        return UserFetcher.constructor(DB.fetch_one(DB.users_table_name, telegram_id=telegram_id))

    @staticmethod
    def fetch_by_id(id: int) -> DbUser:
        return UserFetcher.constructor(DB.fetch_one(DB.users_table_name, id=id))

    @staticmethod
    def constructor(info) -> DbUser | List[DbUser] | None:
        if not info:
            return None

        if isinstance(info, list):
            return [UserFetcher.constructor(user_info) for user_info in info]

        else:
            return DbUser(id=info["id"], telegram_id=info["telegram_id"])

    @staticmethod
    def fetch_date_events(user: DbUser, date: str) -> DbEvent | List[DbEvent] | None:
        return EventFetcher.constructor(DB.fetch_many(DB.events_table_name, date=date, user_id=user.id))


class UserDeleter:
    @staticmethod
    def delete(user: DbUser):
        DB.delete_one(DB.users_table_name, id=user.id)
        DB.delete_one(DB.users_groups_table_name, user_id=user.id)
        DB.delete_one(DB.users_notifications_table_name, user_id=user.id)
        DB.delete_one(DB.users_settings_table_name, user_id=user.id)

    @staticmethod
    def delete_group(user: DbUser, group: DbGroup):
        DB.delete_one(DB.users_groups_table_name, user_id=user.id, group_id=group.id)

    @staticmethod
    def delete_notifications(user: DbUser):
        DB.delete_one(DB.users_notifications_table_name, user_id=user.id)


class UserInserter:
    @staticmethod
    def insert(telegram_id: int):
        DB.insert_one(DB.users_table_name, telegram_id=telegram_id)

        UserInserter.insert_settings(telegram_id=telegram_id)

    @staticmethod
    def insert_group(user: DbUser, group: DbGroup):
        DB.insert_one(DB.users_groups_table_name, group_id=group.id, user_id=user.id)

    @staticmethod
    def insert_settings(telegram_id: int):
        user = UserFetcher.fetch_by_telegram_id(telegram_id=telegram_id)

        UserSettings.insert(user=user)

    @staticmethod
    def insert_notifications(user: DbUser, notifications: List[str] | str):
        if isinstance(notifications, str):
            DB.insert_one(DB.users_notifications_table_name, user_id=user.id, notifications=notifications)

        else:
            for notification in notifications:
                UserInserter.insert_notifications(user=user, notifications=notification)


class UserUpdater:
    @staticmethod
    def update_notifications(user: DbUser, notifications_state: int):
        DB.update_one(DB.users_notifications_table_name, dict(user_id=user.id), dict(value=notifications_state))


class User:
    _user: DbUser
    _user_settings: UserSettings

    def __init__(self, *args, **kwargs):
        kwargs_keys = set(kwargs.keys())

        if kwargs_keys == {"id"}:
            self._user = UserFetcher.fetch_by_id(kwargs["id"])

        elif kwargs_keys == {"telegram_id"}:
            self._user = UserFetcher.fetch_by_telegram_id(kwargs["telegram_id"])

        elif kwargs_keys == {"db_user"}:
            self._user = kwargs["db_user"]

        else:
            raise InvalidUserArgumentsError

        if not self._user:
            raise UserNotFoundError

        self._user_settings = UserSettings(user_id=self._user.id)

    @property
    def settings(self):
        return self._user_settings

    @property
    def notifications(self):
        return UserNotification.user_notifications(user_id=self.id)

    @notifications.setter
    def notifications(self, notifications: List[str] | str):
        UserNotification.delete_user_notifications(user_id=self.id)

        for notification in notifications:
            UserNotification.insert(notification)

    def extract_notifications(self) -> List[UserNotification]:
        notifications = UserNotification.user_notifications(user_id=self.id)
        UserDeleter.delete_notifications(self._user)

        return notifications

    @staticmethod
    def all():
        users = UserFetcher.fetch_all()

        if users:
            return [User(db_user=user_info) for user_info in users]

        return []

    @property
    def id(self) -> int:
        return self._user.id

    @property
    def telegram_id(self) -> int:
        return self._user.telegram_id

    @property
    def groups(self) -> List[Group]:
        return UserFetcher.fetch_groups(self._user)

    @staticmethod
    def insert(telegram_id: int) -> User:
        try:
            User(telegram_id=telegram_id)

            raise UserAlreadyExistsError

        except UserNotFoundError:
            UserInserter.insert(telegram_id=telegram_id)
            user = User(telegram_id=telegram_id)
            UserInserter.insert_notifications(user._user)

            return user

    def delete(self):
        UserDeleter.delete(self._user)
        self._user_settings.delete()

    def insert_group(self, group: Group):
        UserInserter.insert_group(user=self._user, group=group._group)

    def delete_group(self, group: Group):
        UserDeleter.delete_group(self._user, group._group)

    def __str__(self):
        return f"id: {self.id}, telegram_id: {self.telegram_id}"


if __name__ == "__main__":
    pass
