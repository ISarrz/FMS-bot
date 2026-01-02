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
from modules.telegram_int.timetable_handler.sheets_generator import *


@telegram_logger
async def send_weeks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sheets = context.user_data['timetable_sheets']
    if not sheets:
        await update.message.reply_text(text="Расписания нет", reply_markup=None)
        return

    try:
        sheet = sheets[context.user_data['timetable_sheet']]

    except IndexError:
        await update.message.reply_text(text="Расписания нет", reply_markup=None)

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=sheet["title"],
        reply_markup=sheet["reply_markup"]
    )

    context.user_data['timetable_message'] = message


@async_logger
async def update_weeks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sheets = context.user_data['timetable_sheets']

    if not sheets:
        await update.message.reply_text(text="Расписания нет", reply_markup=None)
        return

    try:
        sheet = sheets[context.user_data['timetable_sheet']]

    except IndexError:
        await update.message.reply_text(text="Расписания нет", reply_markup=None)

    message = context.user_data['timetable_message']

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=sheet["title"],
        reply_markup=sheet["reply_markup"]
    )


@telegram_logger
async def send_timetable(update: Update, context: ContextTypes.DEFAULT_TYPE, date: str):
    sheets = context.user_data['timetable_sheets']
    sheet = sheets[context.user_data['timetable_sheet']]
    timetable = sheet["timetables"][date]
    user = User(telegram_id=update.effective_chat.id)

    if user.settings.mode == "image":
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=timetable.image
        )

    elif user.settings.mode == "text":
        await context.bot.send_message(chat_id=update.effective_chat.id, text=timetable.text)
