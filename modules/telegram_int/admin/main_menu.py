from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,

)
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
)
from modules.logger import *
from modules.logger.logger import async_logger, logger

@async_logger
async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sheet = await get_main_menu_sheet(update, context)
    context.chat_data['group'] = 1
    context.chat_data['sheet'] = 0

    await update.message.reply_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


@async_logger
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
