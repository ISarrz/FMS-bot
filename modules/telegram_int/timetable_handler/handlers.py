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
from modules.statistics.statistics import statistic
from modules.telegram_int.timetable_handler.messages import *


@telegram_logger
async def start_timetable_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    statistic.timetable_count += 1
    context.user_data['timetable_sheets'] = get_weeks_sheets(User(telegram_id=update.effective_chat.id))

    User.safe_insert(update.effective_chat.id)
    titles = [sheet["title"] for sheet in context.user_data['timetable_sheets']]

    if "Текущая неделя" in titles:
        context.user_data['timetable_sheet'] = titles.index("Текущая неделя")

    elif "Следующая неделя" in titles:
        context.user_data['timetable_sheet'] = titles.index("Следующая неделя")

    else:
        context.user_data['timetable_sheet'] = 0

    await send_weeks_menu(update, context)
    return 0


@telegram_logger
async def weeks_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == LEFT_ARROW:
        context.user_data["timetable_sheet"] -= 1
        sheets = context.user_data['timetable_sheets']
        context.user_data['timetable_sheet'] += len(sheets)
        context.user_data['timetable_sheet'] %= len(sheets)

        await update_weeks_menu(update, context)

        return 0

    elif income == RIGHT_ARROW:
        context.user_data['timetable_sheet'] += 1
        sheets = context.user_data['timetable_sheets']
        context.user_data['timetable_sheet'] %= len(sheets)

        await update_weeks_menu(update, context)

        return 0

    else:
        await send_timetable(update, context, income)

        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


ConversationHandler_timetable = ConversationHandler(
    entry_points=[CommandHandler('timetable', start_timetable_handler)],

    states={
        0: [CallbackQueryHandler(weeks_menu_handler)]
    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)
