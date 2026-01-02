from modules.time import *
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from modules.database import User
from modules.logger.logger import async_logger, telegram_logger
from modules.telegram_int.constants import *

def get_previous_week_sheet(user: User):
    weekdays = get_previous_week_string_weekdays()
    days = get_previous_week_string_days()

    return get_week_sheet(days, weekdays, user)


def get_current_week_sheet(user: User):
    weekdays = get_current_week_string_weekdays()
    days = get_current_week_string_days()

    return get_week_sheet(days, weekdays, user)


def get_week_sheet(days, weekdays, user):
    timetables = dict()
    keyboard = []
    for i in range(len(days)):
        timetable = user.get_date_timetable(days[i])
        if not timetable or not timetable.image or not timetable.text:
            continue

        timetables[days[i]] = timetable

        keyboard.append([InlineKeyboardButton(text=weekdays[i], callback_data=days[i])])

    if not keyboard:
        return None

    return {
        "keyboard": keyboard,
        "timetables": timetables
    }

def get_next_week_sheet(user: User):
    weekdays = get_next_week_string_weekdays()
    days = get_next_week_string_days()

    return get_week_sheet(days, weekdays, user)


def get_weeks_sheets(user: User):
    sheets = []
    if get_previous_week_sheet(user):
        sheet = get_previous_week_sheet(user)
        sheet["title"] = "Предыдущая неделя"
        sheets.append(sheet)

    if get_current_week_sheet(user):
        sheet = get_current_week_sheet(user)
        sheet["title"] = "Текущая неделя"
        sheets.append(sheet)

    if get_next_week_sheet(user):
        sheet = get_next_week_sheet(user)
        sheet["title"] = "Следующая неделя"
        sheets.append(sheet)

    if len(sheets) > 1:
        for sheet in sheets:
            keyboard = sheet["keyboard"]
            keyboard.append([
                InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
                InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW)
            ])
            sheet["keyboard"] = keyboard

    for sheet in sheets:
        keyboard = sheet["keyboard"]
        sheet["reply_markup"] = InlineKeyboardMarkup(keyboard)

    return sheets