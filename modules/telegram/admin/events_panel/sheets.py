from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
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

from modules.database_api.interaction.fetch import fetch_all_events
from modules.files_api import get_config_field
from modules.database_api import (
    DbGroup,
    DbEvent,
    fetch_all_groups,
    fetch_group_by_id,
    fetch_event_groups_by_id,
    delete_event_by_id,
    fetch_event_by_id,
    fetch_all_events,
)


async def get_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events = [
        DbEvent(id=event['id'], name=event['name'], about=event['about'],
                date=event['date'], start=event['start'],
                end=event['end'], owner=event['owner'], place=event['place'])
        for event in fetch_all_events()]

    for i in range(len(events)):
        groups = fetch_event_groups_by_id(events[i].id)
        groups = [DbGroup(id=group['id'], name=group['name'], about=group['about']) for group in groups]

        events[i] = (events[i], groups)

    sheet_size = 5
    sheets = [[]]
    while events:
        if len(sheets[-1]) > sheet_size:
            sheets.append([])

        sheets[-1].append(events.pop())

    return sheets


async def get_reply_markup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sheets = await get_sheets(update, context)
    cur_sheet = sheets[context.chat_data['sheet']]

    keyboard = []

    for event, groups in cur_sheet:
        if groups:
            groups = ', '.join([group.name for group in groups])
            keyboard.append([InlineKeyboardButton(
                text=f"{event.name}; {event.date}; {event.start}; {groups}",
                callback_data=event.id)])

        else:

            keyboard.append(
                [InlineKeyboardButton(
                    text=f"{event.name}; {event.date}; {event.start}; None",
                    callback_data=event.id)])

    if len(sheets) > 1:
        navigation = [InlineKeyboardButton(text='<-', callback_data='<-'),
                      InlineKeyboardButton(text='+', callback_data='+'),
                      InlineKeyboardButton(text='->', callback_data='->'),
                      ]

    else:
        navigation = [InlineKeyboardButton(text='+', callback_data='+')]

    keyboard.append(navigation)
    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup
