from modules.database.timetable.timetable import Timetable
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
from modules.logger.logger import async_logger

def get_sheet(user: User):
    timetable = []
    weekdays = get_current_week_string_weekdays()
    days = get_current_week_string_days()
    timetable = [(days[i], weekdays[i]) for i in range(len(days)) if user.get_date_timetable(days[i])]

    keyboard = []
    for cur in timetable:
        keyboard.append([InlineKeyboardButton(text=cur[1], callback_data=cur[0])])

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


@async_logger
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    User.safe_insert(update.effective_chat.id)

    context.chat_data['sheet'] = 0
    sheet = get_sheet(User(telegram_id=update.effective_chat.id))
    if sheet.inline_keyboard:
        message = await update.message.reply_text(text="Расписание", reply_markup=sheet)
    else:
        message = await update.message.reply_text(text="Расписания нет", reply_markup=sheet)
    return 0

@async_logger
async def send_timetable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data

    timetable = User(telegram_id=update.effective_chat.id).get_date_timetable(income)

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=timetable.image
    )

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
