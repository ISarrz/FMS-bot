from modules.time import get_current_week_string_days, get_current_week_string_weekdays

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
    filters, CallbackContext
)
from modules.database import User
from modules.logger.logger import async_logger
from modules.telegram_int.constants import set_last_message_id, get_last_message_id
from modules.telegram_int.settings_handler.sheets_generator import *


@async_logger
async def send_settings_menu(update: Update, context: CallbackContext):
    await clear_last_message(update,context)
    sheet = get_settings_menu_sheet(User(telegram_id=update.effective_chat.id))

    message = await update.message.reply_text(text="Настройки", reply_markup=sheet)
    set_last_message_id( update.effective_chat.id,message.message_id)
    context.chat_data['settings_message'] = message


@async_logger
async def update_settings_menu(update: Update, context: CallbackContext):
    message = context.chat_data['settings_message']

    reply_markup = get_settings_menu_sheet(User(telegram_id=update.effective_chat.id))
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text="Настройки",
        reply_markup=reply_markup
    )


@async_logger
async def update_groups_menu(update: Update, context: CallbackContext):
    sheets = get_groups_menu_sheets(update, context)
    ind = context.chat_data['groups_sheet']
    reply_markup = sheets[ind]
    message = context.chat_data['settings_message']
    main_group = context.chat_data['settings_group']
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=f"Группа {main_group.name}",
        reply_markup=reply_markup
    )
