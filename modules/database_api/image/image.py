from __future__ import annotations

from typing import List
from dataclasses import dataclass
from modules.database_api.database.database import DB
from typing import List
from dataclasses import dataclass
from modules.database_api.database.database import DB
from modules.database_api.event.event import EventFetcher
from modules.database_api.group.group_patterns import group_patterns


class ImageNotFoundError(Exception):
    def __str__(self) -> str:
        return "Image not found"


class IncorrectImageArgumentsError(Exception):
    def __str__(self) -> str:
        return "Incorrect image arguments"


@dataclass
class DbImage:
    id: int
    date: str
    image: bytes


class ImageFetcher:
    @staticmethod
    def fetch_all():
        return ImageFetcher.constructor(DB.fetch_many(DB.images_table_name))

    @staticmethod
    def fetch_by_id(id: int):
        return ImageFetcher.constructor(DB.fetch_many(DB.images_table_name, id=id))

    @staticmethod
    def constructor(info):
        if not info:
            return None

        if isinstance(info, list):
            return [ImageFetcher.constructor(image_info) for image_info in info]

        else:
            return DbImage(**dict(info))


class ImageDeleter:
    @staticmethod
    def delete(image: DbImage):
        DB.delete_one(DB.images_table_name, id=image.id)


class Image:
    _image: DbImage

    def __init__(self, *args, **kwargs):
        kwargs_keys = set(kwargs.keys())

        if kwargs_keys == {"id"}:
            self._group = ImageFetcher.fetch_by_id(kwargs.get("id"))


        elif kwargs_keys == {"db_image"}:
            self._group = kwargs.get("db_image")

        else:
            raise IncorrectImageArgumentsError()

        if not self._group:
            raise ImageNotFoundError

    @property
    def id(self) -> int:
        return self._image.id

    @property
    def date(self) -> str:
        return self._image.date

    @property
    def image(self) -> DbImage:
        return self._image

    def delete(self):
        ImageDeleter.delete(self._image)
