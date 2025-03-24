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
    filters,

)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from modules.files_api import get_config_field
from modules.database_api import *

async def get_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    groups = [DbGroup(id=group['id'], name=group['name'], about=group['about']) for group in fetch_all_groups()]
    sheet_size = 5
    sheets = [[]]
    while groups:
        if len(sheets[-1]) > sheet_size:
            sheets.append([])

        sheets[-1].append(groups.pop())

    return sheets


async def get_reply_markup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sheets = await get_sheets(update, context)
    cur_sheet = sheets[context.chat_data['sheet']]

    keyboard = []

    for group in cur_sheet:
        parents = fetch_groups_sequence(group.id)

        if len(parents) > 1:
            parents = parents[1:]
            parents_info = '; '.join([f"({i['id']}) {i['name']}" for i in parents])

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
