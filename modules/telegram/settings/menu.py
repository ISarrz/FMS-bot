from __future__ import annotations
from typing import List
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes
from modules.database.user import User
from modules.database.database import db
from modules.database.group import Group
from modules.database.type import Type



def get_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['group_sheet'] = 0

    notif_state = User(db, telegram_id=update.effective_user.id).settings['notification']
    notification_text = 'Уведомления: +' if notif_state else 'Уведомления: -'

    keyboard = [
        [InlineKeyboardButton(text='Группы', callback_data='group')],
        [InlineKeyboardButton(text=notification_text, callback_data='notification')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = 'Настройки'

    return text, reply_markup


def group_sheets() -> List[List[Group]]:

    sheets = []
    cur_sheet = []

    for group in Group.getall(db):

        different_types_check = cur_sheet and group.type.id != cur_sheet[-1].type.id
        len_check = len(cur_sheet) >= 5

        if len_check or different_types_check:
            sheets.append(cur_sheet)
            cur_sheet = []

        cur_sheet.append(group)

    return sheets


def get_group_menu(update: Update, context: ContextTypes):
    sheets = group_sheets()
    user = User(db, telegram_id=update.effective_user.id)
    user_groups = user.groups

    keyboard = []
    text = 'Группы'

    if sheets:
        context.user_data['sheet'] = (context.user_data['sheet'] + len(sheets) - 1) % len(sheets)

        cur_sheet = sheets[context.user_data['sheet']]
        text = cur_sheet[0].type.name

        for group in cur_sheet:
            is_user_group = group in user_groups
            row_text = f'{group.name} {'+' if is_user_group else '-'}'
            keyboard.append([InlineKeyboardButton(row_text, callback_data=f'{group.id}, {int(is_user_group)}')])

    navigation = [InlineKeyboardButton(text='<!>', callback_data='back')]

    if len(sheets) > 1:
        navigation.insert(0, InlineKeyboardButton(text='<-', callback_data='left'))
        navigation.append(InlineKeyboardButton(text='->', callback_data='right'))
    keyboard.append(navigation)
    reply_markup = InlineKeyboardMarkup(keyboard)

    return text, reply_markup
