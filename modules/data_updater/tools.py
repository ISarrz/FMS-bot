from modules.database import Group, User, Event
from dataclasses import dataclass
from typing import List, Self

@dataclass
class NodeGroup:
    title: str


@dataclass
class CategoryGroup(NodeGroup):
    children: List[NodeGroup]


@dataclass
class EventsGroup(NodeGroup):
    events: List[Event]




class GroupTimetable:
    title: str
    events:List[Event]
    children: List[Self]

    def __init__ (self, title:str, events:List[Event], children:List[Self] | None):
        self.title = title
        self.events = events
        self.children = children

def group_is_class_group(group: Group):
    if not group.parent:
        return False

    if not group.parent.parent:
        return False

    if group.parent.parent.id == Group(name="10 класс").id:
        return True
    if group.parent.parent.id == Group(name="11 класс").id:
        return True

    return False


def group_is_class(group: Group):
    if not group.parent:
        return False

    if group.parent.id == Group(name="10 класс").id:
        return True

    if group.parent.id == Group(name="11 класс").id:
        return True

    return False


def group_is_course(group: Group):
    if not group.parent:
        return False

    return group.parent.id == Group(name="Спецкурсы").id


def group_is_club(group: Group):
    if not group.parent:
        return False

    return group.parent.id == Group(name="Клубы").id


def get_user_clubs(user: User):
    result = []
    for group in user.groups:
        if group_is_class(group):
            result.append(group)

    return result


def group_is_academic_group(group: Group):
    if "группа" not in group.name:
        return False

    if not group.parent:
        return False

    if group.parent.id == Group(name="10 класс").id:
        return True

    if group.parent.id == Group(name="11 класс").id:
        return True

    return False


def get_user_courses_events(user: User, date: str):
    result = []
    for group in user.groups:
        if not group_is_course(group):
            continue

        events = group.get_date_events(date)
        result += events

    return result


def normalize_string(string: str):
    MAX_LENGTH = 20
    lines = []
    cur_line = ""
    for word in string.split():
        if len(cur_line + " " + word) > MAX_LENGTH:
            if cur_line:
                lines.append(cur_line)
            cur_line = word
        else:
            cur_line += " " + word

    if cur_line:
        lines.append(cur_line)

    return lines


def user_in_all_subgroups(user: User, group: Group):
    user_groups_ids = set([user_group.id for user_group in user.groups])
    children_ids = set([child.id for child in group.children])

    return children_ids.issubset(user_groups_ids)


def normalize_value(value: str) -> str:
    lines = value.split("\n")
    result = []
    for line in lines:
        for new_line in normalize_string(line):
            result.append(new_line)

    return "\n".join(result)



@dataclass
class Sheet:
    title: str
    events: List[Event]