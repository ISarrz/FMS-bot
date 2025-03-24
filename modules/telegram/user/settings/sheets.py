from __future__ import annotations
from typing import List
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes
from modules.database_api import *


# from modules.database.user import User
# from modules.database.database import db
# from modules.database.group import Group
# from modules.database.type import Type


def get_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['group_sheet'] = 0

    # notif_state = User(db, telegram_id=update.effective_user.id).settings['notification']
    # notification_text = 'Уведомления: +' if notif_state else 'Уведомления: -'

    keyboard = [
        [InlineKeyboardButton(text='Группы', callback_data='group')],
        # [InlineKeyboardButton(text=notification_text, callback_data='notification')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


def get_user_groups_sheets(user_id):
    sheets = []
    cur_sheet = []

    user_groups = [DbGroup(id=group['id'], name=group['name'], about=group['about'])
                   for group in fetch_user_groups_by_id(user_id)]

    sheet_size = 5
    sheets = [[]]
    while user_groups:
        if len(sheets[-1]) > sheet_size:
            sheets.append([])

        sheets[-1].append(user_groups.pop())

    return sheets


def get_group_menu(update: Update, context: ContextTypes):
    telegram_id = update.effective_user.id
    user = fetch_user_by_telegram_id(telegram_id)

    sheets = get_user_groups_sheets(user['id'])

    keyboard = []

    for group in sheets:
        parents = fetch_groups_sequence(group.id)

        if len(parents) > 1:
            parents = parents[1:]
            parents_info = '; '.join([f"{i['name']}" for i in parents])

        else:
            parents_info = ""

        keyboard.append([InlineKeyboardButton(text=f"{group.name} | {parents_info}", callback_data=group.id)])

    if len(sheets) > 1:
        navigation = [InlineKeyboardButton(text='←', callback_data='<-'),
                      InlineKeyboardButton(text='+', callback_data='+'),
                      InlineKeyboardButton(text='→', callback_data='->'),
                      ]

    else:
        navigation = [InlineKeyboardButton(text='+', callback_data='+')]

    keyboard.append(navigation)
    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


def get_groups_selection(update: Update, context: ContextTypes):
    pass
