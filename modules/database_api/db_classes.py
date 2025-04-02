from dataclasses import dataclass

@dataclass
class DbUser:
    id: int
    telegram_id: int


@dataclass
class Event:
    name: str
    about: str
    date: str
    start: str
    end: str
    owner: str
    place: str

@dataclass
class DbEvent(Event):
    id: int

@dataclass
class Group:
    name: str
    about: str

@dataclass
class DbGroup(Group):
    id: int
