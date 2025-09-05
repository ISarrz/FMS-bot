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
    filters
)
from modules.database import User
from modules.logger.logger import async_logger


def get_sheet(user: User):
    timetables = []
    weekdays = get_current_week_string_weekdays()
    days = get_current_week_string_days()
    keyboard = []
    for i in range(len(days)):
        timetable = user.get_date_timetable(days[i])
        if not timetable or timetable is None:
            continue

        if not timetable.image or timetable.image is None:
            continue

        if not timetable.text or timetable.text is None:
            continue

        keyboard.append([InlineKeyboardButton(text=weekdays[i], callback_data=days[i])])

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


@async_logger
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    User.safe_insert(update.effective_chat.id)

    sheet = get_sheet(User(telegram_id=update.effective_chat.id))
    if sheet.inline_keyboard:
        message = await update.message.reply_text(text="Расписание", reply_markup=sheet)

    else:
        message = await update.message.reply_text(text="Расписания нет", reply_markup=None)

    return 0


@async_logger
async def send_timetable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data

    user = User(telegram_id=update.effective_chat.id)
    timetable = user.get_date_timetable(income)

    if timetable is None or timetable.text is None or timetable.image is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Ошибка расписания"
        )

    elif user.settings.mode == "image":
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=timetable.image
        )

    elif user.settings.mode == "text":
        await context.bot.send_message(chat_id=update.effective_chat.id, text=timetable.text)

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


ConversationHandler_timetable = ConversationHandler(
    entry_points=[CommandHandler('timetable', start)],

    states={
        0: [CallbackQueryHandler(send_timetable)],

    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)
