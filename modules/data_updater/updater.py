from modules.database import User, Group, Timetable
from modules.time.dates import get_current_string_dates

from modules.data_updater.tools import (
    group_is_class,
    group_is_academic_group,
    get_user_courses_events,
    user_in_all_subgroups,
    EventsGroup,
    CategoryGroup
)

from modules.data_updater.image_generator import (
    get_timetable_image
)
from modules.data_updater.text_generator import (
    get_timetable_text
)


def update():
    for user in User.all():
        if user.id == 2:
            update_user(user)


def update_user(user: User):
    dates = []

    for date in get_current_string_dates():
        date_is_updated = False
        for group in user.groups:
            if group_is_academic_group(group):
                parent = group.parent
                title = f"{parent.name} {group.name}"
                date_is_updated |= update_user_group(user=user, title=title, group=group, date=date)

            elif group_is_class(group):
                date_is_updated |= update_user_class(user, group, date)

        date_is_updated |= update_user_clubs(user, date, rewrite=date_is_updated)
        if date_is_updated:
            dates.append(date)

    if not dates:
        return

    notif = [notification.value for notification in user.notifications]
    notif.append(f"Доступно расписание на {', '.join(dates)}")
    user.notifications = notif


def update_user_group(user: User, title: str, group: Group, date: str) -> bool:
    group_events = group.get_date_events(date)
    course_events = get_user_courses_events(user, date)
    events = group_events + course_events

    group_root = EventsGroup(title=title, events=events)
    course_root = EventsGroup(title=title, events=course_events)

    # check if timetable already exists
    text = get_timetable_text(group_root, date)
    if not group_events:
        return False

    if not events or Timetable.exist(user_id=user.id, date=date, text=text):
        return False

    # delete timetable without group events
    course_text = get_timetable_text(course_root, date)

    if group_events and Timetable.exist(user_id=user.id, date=date, text=course_text):
        Timetable(date=date, user_id=user.id, text=course_text).delete()

    image = get_timetable_image(group_root, date)
    user.insert_timetable(date=date, image=image, text=text)

    return True


def update_user_class(user: User, group: Group, date: str):
    if user_in_all_subgroups(user, group):
        course_events = sorted(get_user_courses_events(user, date))
        title = f"{group.parent.name} {group.name}"
        class_root = CategoryGroup(title=title, children=[])
        class_have_events = False
        for child in group.children:
            child_events = child.get_date_events(date)

            class_root.children.append(EventsGroup(title=child.name, events=sorted(child_events + course_events)))

            if child_events:
                class_have_events = True

        # check if timetable already exists
        text = get_timetable_text(class_root, date)
        if not class_have_events:
            return False

        if Timetable.exist(user_id=user.id, date=date, text=text):
            return False

        # delete timetable without group events
        course_root = CategoryGroup(title=group.name, children=[])
        for child in group.children:
            course_root.children.append(EventsGroup(title=child.name, events=course_events))

        course_text = get_timetable_text(root=course_root, date=date)

        if class_have_events and Timetable.exist(user_id=user.id, date=date, text=course_text):
            Timetable(date=date, user_id=user.id, text=course_text).delete()

        # generate image
        image = get_timetable_image(class_root, date)
        user.insert_timetable(date=date, image=image, text=text)

        return True

    else:
        updated = False
        for child in user.get_subgroups(group):
            grade = group.parent
            title = ""
            if "11" in grade.name:
                title += "11 "

            elif "10" in grade.name:
                title += "10 "

            title += f"{group.name} {child.name}"

            updated |= update_user_group(user=user, title=title, group=child, date=date)

    return updated


def update_user_clubs(user: User, date: str, rewrite=False):
    group = Group(name="Клубы")
    user_clubs = user.get_subgroups(group)
    events = []
    for club in user_clubs:
        events += club.get_date_events(date)

    if not events:
        return False

    events = sorted(events)

    clubs_root = EventsGroup(title=group.name, events=events)
    text = get_timetable_text(clubs_root, date)
    if rewrite and Timetable.exist(user_id=user.id, date=date, text=text):
        Timetable(date=date, user_id=user.id, text=text).delete()

    elif not rewrite and Timetable.exist(user_id=user.id, date=date, text=text):
        return False

    image = get_timetable_image(clubs_root, date)
    user.insert_timetable(date=date, image=image, text=text)

    return True


def get_root(group: Group, date: str):
    if group.children:
        root = CategoryGroup(title=group.name, children=[])
        for child in group.children:
            root.children.append(get_root(child, date))

        return root

    root = EventsGroup(title=group.name, events=group.get_date_events(date))

    return root


import time

if __name__ == '__main__':
    start_time = time.perf_counter()
    update()
    end_time = time.perf_counter()
    print(f"Затраченное время: {end_time - start_time:0.10f} сек")
    # group = Group(id=6)
    # date = "14.01.2026"
    #
    # root = get_root(group, date)
    #
    # start_time = time.perf_counter()
    # image = get_timetable_image(root, date)
    # end_time = time.perf_counter()
    # print(f"Затраченное время: {end_time - start_time:0.10f} сек")
    #
    # start_time = time.perf_counter()
    # text = get_timetable_text(root, date)
    # end_time = time.perf_counter()
    # print(f"Затраченное время: {end_time - start_time:0.10f} сек")
