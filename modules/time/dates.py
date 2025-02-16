import datetime as dt
import pytz

# Krasnoyarsk
timezone = pytz.timezone('Etc/GMT-7')


def get_current_week():
    now = dt.datetime.now(timezone)
    cur_monday = now - dt.timedelta(days=now.weekday())

    return [cur_monday + dt.timedelta(days=day) for day in range(7)]


def get_last_week():
    now = dt.datetime.now(timezone)
    cur_monday = now - dt.timedelta(days=now.weekday())
    last_monday = cur_monday - dt.timedelta(days=7)

    return [last_monday + dt.timedelta(days=day) for day in range(7)]


def get_next_week():
    now = dt.datetime.now(timezone)
    cur_monday = now - dt.timedelta(days=now.weekday())
    next_monday = cur_monday + dt.timedelta(days=7)

    return [next_monday + dt.timedelta(days=day) for day in range(7)]


if __name__ == '__main__':
    print(dt.datetime.now(timezone))
