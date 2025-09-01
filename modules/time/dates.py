import datetime as dt
import pytz

# Krasnoyarsk
timezone = pytz.timezone('Etc/GMT-7')
NUMBERS_TO_WEEKDAYS = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье"
}

MAX_WEEKDAY_LENGTH = max(len(weekday) for weekday in NUMBERS_TO_WEEKDAYS.values())
WEEKDAY_PADDING = 2


def get_current_week():
    now = dt.datetime.now(timezone)
    now = dt.datetime.strptime("14.04.2025", "%d.%m.%Y")

    cur_monday = now - dt.timedelta(days=now.weekday())

    return [cur_monday + dt.timedelta(days=day) for day in range(7)]


def get_next_week():
    now = dt.datetime.now(timezone)
    now = dt.datetime.strptime("14.04.2025", "%d.%m.%Y")

    cur_monday = now - dt.timedelta(days=now.weekday())
    next_monday = cur_monday + dt.timedelta(days=7)

    return [next_monday + dt.timedelta(days=day) for day in range(7)]


def get_previous_week():
    now = dt.datetime.now(timezone)
    now = dt.datetime.strptime("14.04.2025", "%d.%m.%Y")

    cur_monday = now - dt.timedelta(days=now.weekday())
    previous_monday = cur_monday - dt.timedelta(days=7)

    return [previous_monday + dt.timedelta(days=day) for day in range(7)]


def get_current_week_string_days():
    current_dates = get_current_week()
    current_string_dates = [date.strftime('%d.%m') for date in current_dates]

    return current_string_dates


def get_next_week_string_days():
    current_dates = get_next_week()
    current_string_dates = [date.strftime('%d.%m') for date in current_dates]

    return current_string_dates


def get_current_string_dates():
    current_dates = get_current_week() + get_next_week()
    current_string_dates = [date.strftime('%d.%m.%Y') for date in current_dates]

    return current_string_dates


def get_current_week_string_weekdays():
    current_dates = get_current_week()
    current_string_weekdays = []
    for date in current_dates:
        padding = MAX_WEEKDAY_LENGTH - len(NUMBERS_TO_WEEKDAYS[date.weekday()])
        current_string_weekdays.append(
            NUMBERS_TO_WEEKDAYS[date.weekday()] + " " * int(padding * 2.3 + 2) + date.strftime('%d.%m'))

    return current_string_weekdays


def get_next_week_string_weekdays():
    current_dates = get_next_week()
    current_string_weekdays = []
    for date in current_dates:
        padding = MAX_WEEKDAY_LENGTH - len(NUMBERS_TO_WEEKDAYS[date.weekday()])
        current_string_weekdays.append(
            NUMBERS_TO_WEEKDAYS[date.weekday()] + " " * int(padding * 2.3 + 2) + date.strftime('%d.%m'))

    return current_string_weekdays


if __name__ == '__main__':
    weekdays = get_current_week()
    for i in get_current_week_string_weekdays():
        print(i)
