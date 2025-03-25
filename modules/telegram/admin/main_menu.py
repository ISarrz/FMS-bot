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
from modules.time import *


from modules.telegram.admin.symbols import *


async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sheet = await get_main_menu_sheet(update, context)
    context.chat_data['group'] = 1
    context.chat_data['sheet'] = 0

    await update.message.reply_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def update_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    sheet = await get_main_menu_sheet(update, context)
    context.chat_data['group'] = 1
    context.chat_data['sheet'] = 0

    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def get_main_menu_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(text="Группы", callback_data="groups")],
                [InlineKeyboardButton(text="События", callback_data="events")]
                ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    sheet = {"text": "Панель администратора", "reply_markup": reply_markup}

    return sheet
