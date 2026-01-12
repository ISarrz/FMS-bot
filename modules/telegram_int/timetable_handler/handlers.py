from modules.telegram_int.timetable_handler.messages import (
    send_weeks_menu,
    send_timetable_menu,
    update_weeks_menu
)
from modules.telegram_int.constants import get_last_message_id, clear_last_message
from modules.telegram_int.constants import LEFT_ARROW, RIGHT_ARROW, BACK_ARROW
from modules.telegram_int.timetable_handler.sheets_generator import (
    get_weeks_sheets,
    get_timetable_sheets,

)
from telegram import (
    Update

)

from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CallbackContext
)
from modules.database import User
from modules.logger.logger import telegram_logger
from modules.statistics.statistics import statistic

WEEKS_MENU_HANDLER = 0
TIMETABLE_MENU_HANDLER = 1


async def get_week_sheet_ind(context: CallbackContext):
    titles = [sheet["text"] for sheet in context.user_data["weeks_sheets"]]
    if "Текущая неделя" in titles:
        return titles.index("Текущая неделя")

    elif "Следующая неделя" in titles:
        return titles.index("Следующая неделя")

    elif "Предыдущая неделя" in titles:
        return titles.index("Предыдущая неделя")

    return -1


@telegram_logger
async def start_timetable_handler(update: Update, context: CallbackContext):
    await clear_last_message(update,context)


    statistic.timetable_count += 1
    context.user_data["weeks_sheets"] = get_weeks_sheets(User(telegram_id=update.effective_chat.id))

    User.safe_insert(update.effective_chat.id)
    ind = await get_week_sheet_ind(context)
    if  ind != -1:
        context.user_data["week_sheet_ind"] = ind

    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Расписания нет",
            reply_markup=None
        )

        return ConversationHandler.END

    await send_weeks_menu(update, context)

    return WEEKS_MENU_HANDLER


@telegram_logger
async def weeks_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == LEFT_ARROW:
        context.user_data["week_sheet_ind"] -= 1
        sheets = context.user_data["weeks_sheets"]
        context.user_data["week_sheet_ind"] += len(sheets)
        context.user_data["week_sheet_ind"] %= len(sheets)

        await update_weeks_menu(context)

        return WEEKS_MENU_HANDLER

    elif income == RIGHT_ARROW:
        context.user_data["week_sheet_ind"] += 1
        sheets = context.user_data["weeks_sheets"]
        context.user_data["week_sheet_ind"] %= len(sheets)

        await update_weeks_menu(context)

        return WEEKS_MENU_HANDLER

    else:
        context.user_data["date"] = income
        context.user_data["timetable_sheet_ind"] = 0
        context.user_data["timetable_sheets"] = get_timetable_sheets(update, context)

        await send_timetable_menu(update, context)

        return TIMETABLE_MENU_HANDLER


@telegram_logger
async def timetable_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == LEFT_ARROW:
        context.user_data["timetable_sheet_ind"] -= 1
        sheets = context.user_data["timetable_sheets"]
        context.user_data["timetable_sheet_ind"] += len(sheets)
        context.user_data["timetable_sheet_ind"] %= len(sheets)

        await send_timetable_menu(update, context)

        return TIMETABLE_MENU_HANDLER

    elif income == RIGHT_ARROW:
        context.user_data["timetable_sheet_ind"] += 1
        sheets = context.user_data["timetable_sheets"]
        context.user_data["timetable_sheet_ind"] %= len(sheets)

        await send_timetable_menu(update, context)

        return TIMETABLE_MENU_HANDLER

    elif income == BACK_ARROW:
        ind = await get_week_sheet_ind(context)
        if ind != -1:
            context.user_data["week_sheet_ind"] = ind

        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Расписания нет",
                reply_markup=None
            )

            return ConversationHandler.END

        await send_weeks_menu(update, context)

        return WEEKS_MENU_HANDLER

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext):
    if update.callback_query:
        await update.callback_query.message.edit_reply_markup(None)

    return ConversationHandler.END


ConversationHandler_timetable = ConversationHandler(
    entry_points=[CommandHandler("timetable", start_timetable_handler)],

    states={
        WEEKS_MENU_HANDLER: [CallbackQueryHandler(weeks_menu_handler)],
        TIMETABLE_MENU_HANDLER: [CallbackQueryHandler(timetable_menu_handler)]
    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)
