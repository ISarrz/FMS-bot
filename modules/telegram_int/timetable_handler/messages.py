from telegram import (
    Update
)
from telegram.ext import (
    ContextTypes
)
from modules.telegram_int.constants import set_last_message_id, clear_last_message
from modules.database import User
from modules.logger.logger import async_logger, telegram_logger


@telegram_logger
async def send_weeks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await clear_last_message(update, context)
    sheets = context.user_data["weeks_sheets"]
    sheet = sheets[context.user_data["week_sheet_ind"]]

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=sheet["text"],
        reply_markup=sheet["reply_markup"]
    )
    set_last_message_id(update.effective_chat.id, message.message_id)
    context.user_data["timetable_message"] = message


@async_logger
async def update_weeks_menu(context: ContextTypes.DEFAULT_TYPE):
    sheets = context.user_data["weeks_sheets"]
    sheet = sheets[context.user_data["week_sheet_ind"]]

    message = context.user_data["timetable_message"]

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=sheet["text"],
        reply_markup=sheet["reply_markup"]
    )


@telegram_logger
async def send_timetable_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await clear_last_message(update, context)
    sheets = context.user_data["timetable_sheets"]
    sheet = sheets[context.user_data["timetable_sheet_ind"]]
    user = User(telegram_id=update.effective_chat.id)

    if user.settings.mode == "image":
        message = await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=sheet["timetable"].image,
            reply_markup=sheet["reply_markup"]
        )
        set_last_message_id(update.effective_chat.id, message.message_id)

    elif user.settings.mode == "text":
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=sheet["timetable"].text,
            reply_markup=sheet["reply_markup"]
        )
        set_last_message_id(update.effective_chat.id, message.message_id)
