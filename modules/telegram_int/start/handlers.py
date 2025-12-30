from modules.config import get_telegram_message
from modules.database import Group, User
from modules.logger.logger import async_logger
from modules.statistics.statistics import get_statistics_field, set_statistics_field
from modules.telegram_int.start.sheets_generator import (get_ten_grade_sheet, get_eleven_grade_sheet,
                                                         get_eleven_grade_academic_groups_sheet,
                                                         get_ten_grade_academic_groups_sheet)

from modules.telegram_int.start.messages import send_grade_menu

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

GRADE_MENU_HANDLER = 0
SCHOOL_CLASS_HANDLER = 1
CLASS_GROUP_HANDLER = 2
ACADEMIC_GROUP_HANDLER = 3
END_HANDLER = 4


@async_logger
async def start(update: Update, context: CallbackContext):
    count = get_statistics_field("start_count")
    set_statistics_field("start_count", count + 1)

    await send_grade_menu(update, context)
    User.safe_insert(update.effective_chat.id)

    return GRADE_MENU_HANDLER


@async_logger
async def grade_menu(update: Update, context: CallbackContext):
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

    return SCHOOL_CLASS_HANDLER


@async_logger
async def school_class_menu(update: Update, context: CallbackContext):
    message = context.chat_data["start_message"]
    query = update.callback_query
    await query.answer()
    income = query.data
    context.chat_data["grade"] = income
    if income == "10 класс":
        reply_markup = await get_ten_grade_sheet()
    if income == "11 класс":
        reply_markup = await get_eleven_grade_sheet()

    text = get_telegram_message("class")
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )

    return CLASS_GROUP_HANDLER


@async_logger
async def class_group_menu(update: Update, context: CallbackContext):
    message = context.chat_data["start_message"]
    query = update.callback_query
    await query.answer()
    income = query.data
    context.chat_data["class"] = income
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

    return ACADEMIC_GROUP_HANDLER


@async_logger
async def academic_group_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = context.chat_data["start_message"]
    query = update.callback_query
    await query.answer()
    income = query.data
    context.chat_data["class_group"] = income

    reply_markup = None
    if income == "10 класс":
        reply_markup = await get_ten_grade_academic_groups_sheet()

    elif income == "11 класс":
        reply_markup = await  get_eleven_grade_academic_groups_sheet()

    text = get_telegram_message("academic_group")
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )

    return END_HANDLER


@async_logger
async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = context.chat_data["start_message"]
    query = update.callback_query
    await query.answer()
    income = query.data
    context.chat_data["academic_group"] = income

    text = get_telegram_message("start_end")
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=None
    )

    user = User(telegram_id=update.effective_chat.id)
    grade = Group(name=context.chat_data["grade"])
    school_class = Group(name=context.chat_data["class"])
    class_group = Group(name=context.chat_data["class_group"], parent=school_class)
    academic_group = Group(name=context.chat_data["academic_group"], parent=grade)
    for group in user.groups:
        user.delete_group(group)

    for timetable in user.timetable:
        timetable.delete()

    user.insert_group(grade)
    user.insert_group(school_class)
    user.insert_group(class_group)
    user.insert_group(academic_group)

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


ConversationHandler_start = ConversationHandler(
    entry_points=[CommandHandler('start', start)],

    states={
        0: [CallbackQueryHandler(grade_menu)],
        1: [CallbackQueryHandler(school_class_menu)],
        2: [CallbackQueryHandler(class_group_menu)],
        3: [CallbackQueryHandler(academic_group_menu)],
        4: [CallbackQueryHandler(end)],
    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)
