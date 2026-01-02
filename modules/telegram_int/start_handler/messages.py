from modules.config import get_telegram_message
from modules.database import Group, User
from modules.logger.logger import async_logger

from modules.telegram_int.start_handler.sheets_generator import (
    get_ten_grade_sheet, get_eleven_grade_sheet,
    get_eleven_grade_academic_groups_sheet,
    get_ten_grade_academic_groups_sheet
)

from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
    CallbackContext,
)
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


@async_logger
async def send_start_menu(update: Update, context: CallbackContext):
    text = get_telegram_message("info")

    keyboard = []
    keyboard.append([InlineKeyboardButton(text="Далее", callback_data="1")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = await update.message.reply_text(text=text, reply_markup=reply_markup)
    context.chat_data["start_message"] = message


@async_logger
async def update_grade_menu(update: Update, context: CallbackContext):
    message = context.chat_data["start_message"]
    keyboard = []
    keyboard.append([InlineKeyboardButton(text="11 класс", callback_data="11 класс")])
    keyboard.append([InlineKeyboardButton(text="10 класс", callback_data="10 класс")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = get_telegram_message("grade")
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )


@async_logger
async def update_school_class_menu(update: Update, context: CallbackContext):
    message = context.chat_data["start_message"]
    grade = context.chat_data["grade"]

    if grade == "10 класс":
        reply_markup = await get_ten_grade_sheet()

    if grade == "11 класс":
        reply_markup = await get_eleven_grade_sheet()

    text = get_telegram_message("class")
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )


@async_logger
async def update_class_group_menu(update: Update, context: CallbackContext):
    message = context.chat_data["start_message"]

    keyboard = []
    if context.chat_data["grade"] == "10 класс":
        keyboard.append([
            InlineKeyboardButton(text="Группа A", callback_data="Группа А"),
            InlineKeyboardButton(text="Группа Б", callback_data="Группа Б")
        ])

    if context.chat_data["grade"] == "11 класс":
        keyboard.append([
            InlineKeyboardButton(text="Группа IT", callback_data="Группа IT"),
            InlineKeyboardButton(text="Группа Физмат", callback_data="Группа Физмат")
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = get_telegram_message("class_group")
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )


@async_logger
async def update_academic_group_menu(update: Update, context: CallbackContext):
    message = context.chat_data["start_message"]

    reply_markup = None
    if context.chat_data["grade"] == "10 класс":
        reply_markup = await get_ten_grade_academic_groups_sheet()

    elif context.chat_data["grade"] == "11 класс":
        reply_markup = await  get_eleven_grade_academic_groups_sheet()

    text = get_telegram_message("academic_group")
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )


@async_logger
async def update_end_menu(update: Update, context: CallbackContext):
    message = context.chat_data["start_message"]

    text = get_telegram_message("start_end")
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=None
    )
