from modules.time import (
    get_current_week_string_days,
    get_current_week_string_weekdays,
    get_previous_week_string_days,
    get_previous_week_string_weekdays,
    get_next_week_string_days,
    get_next_week_string_weekdays,
)
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes
)
from modules.database import User
from modules.telegram_int.constants import LEFT_ARROW, RIGHT_ARROW, BACK_ARROW


def get_previous_week_sheet(user: User):
    weekdays = get_previous_week_string_weekdays()
    days = get_previous_week_string_days()

    return get_week_sheet(days, weekdays, user)


def get_current_week_sheet(user: User):
    weekdays = get_current_week_string_weekdays()
    days = get_current_week_string_days()

    return get_week_sheet(days, weekdays, user)


def get_next_week_sheet(user: User):
    weekdays = get_next_week_string_weekdays()
    days = get_next_week_string_days()

    return get_week_sheet(days, weekdays, user)


def get_week_sheet(days, weekdays, user: User):
    keyboard = []

    for i in range(len(days)):
        if user.get_date_timetable(days[i]):
            keyboard.append([InlineKeyboardButton(text=weekdays[i], callback_data=days[i])])

    return keyboard if keyboard else None


def get_weeks_sheets(user: User):
    sheets = []

    if week := get_previous_week_sheet(user):
        sheets.append({"keyboard": week, "text": "Предыдущая неделя"})

    if week := get_current_week_sheet(user):
        sheets.append({"keyboard": week, "text": "Текущая неделя"})

    if week := get_next_week_sheet(user):
        sheets.append({"keyboard": week, "text": "Следующая неделя"})

    for sheet in sheets:
        if len(sheets) > 1:
            sheet["keyboard"].append([
                InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
                InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW)
            ])

        sheet["reply_markup"] = InlineKeyboardMarkup(sheet["keyboard"])

    return sheets


def get_timetable_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = User(telegram_id=update.effective_user.id)
    date = context.user_data["date"]
    timetable = user.get_date_timetable(date)

    sheets = []

    for cur_timetable in timetable:
        data = dict()
        data["timetable"] = cur_timetable
        if len(timetable) > 1:
            keyboard = [[
                InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
                InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
                InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW)
            ]]

        else:
            keyboard = [[
                InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW)
            ]]

        data["reply_markup"] = InlineKeyboardMarkup(keyboard)

        sheets.append(data)

    return sheets
