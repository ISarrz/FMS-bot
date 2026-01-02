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
# SET_DATE = None
SET_DATE = dt.datetime.strptime("15.12.2025", "%d.%m.%Y")


def get_string_dates(dates):
    string_dates = [date.strftime('%d.%m.%Y') for date in dates]

    return string_dates


def get_string_weekdays(dates):
    string_weekdays = []
    for date in dates:
        padding = MAX_WEEKDAY_LENGTH - len(NUMBERS_TO_WEEKDAYS[date.weekday()])
        string_weekdays.append(
            NUMBERS_TO_WEEKDAYS[date.weekday()] + " " * int(padding * 2.3 + 2) + date.strftime('%d.%m'))

    return string_weekdays


def get_previous_week():
    if SET_DATE:
        now = SET_DATE
    else:
        now = dt.datetime.now(timezone)

    cur_monday = now - dt.timedelta(days=now.weekday())
    previous_monday = cur_monday - dt.timedelta(days=7)

    return [previous_monday + dt.timedelta(days=day) for day in range(7)]


def get_previous_week_string_days():
    return get_string_dates(get_previous_week())


def get_previous_week_string_weekdays():
    return get_string_weekdays(get_previous_week())


def get_current_week():
    if SET_DATE:
        now = SET_DATE
    else:
        now = dt.datetime.now(timezone)

    cur_monday = now - dt.timedelta(days=now.weekday())

    return [cur_monday + dt.timedelta(days=day) for day in range(7)]


def get_current_week_string_days():
    return get_string_dates(get_current_week())


def get_current_week_string_weekdays():
    return get_string_weekdays(get_current_week())


def get_next_week():
    if SET_DATE:
        now = SET_DATE
    else:
        now = dt.datetime.now(timezone)

    cur_monday = now - dt.timedelta(days=now.weekday())
    next_monday = cur_monday + dt.timedelta(days=7)

    return [next_monday + dt.timedelta(days=day) for day in range(7)]


def get_next_week_string_days():
    return get_string_dates(get_next_week())


def get_next_week_string_weekdays():
    current_dates = get_next_week()
    current_string_weekdays = []
    for date in current_dates:
        padding = MAX_WEEKDAY_LENGTH - len(NUMBERS_TO_WEEKDAYS[date.weekday()])
        current_string_weekdays.append(
            NUMBERS_TO_WEEKDAYS[date.weekday()] + " " * int(padding * 2.3 + 2) + date.strftime('%d.%m'))

    return current_string_weekdays


def get_current_string_dates():
    return get_string_dates(get_previous_week() + get_current_week() + get_next_week())


if __name__ == '__main__':
    weekdays = get_current_week()
    for i in get_current_week_string_weekdays():
        print(i)
