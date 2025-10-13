from modules.config import get_telegram_message
from modules.database import Group, User
from modules.logger.logger import async_logger
from modules.statistics.statistics import get_statistics_field, set_statistics_field

from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


@async_logger
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = get_statistics_field("start_count")
    set_statistics_field("start_count", count + 1)

    text = get_telegram_message("info")

    keyboard = []
    keyboard.append([InlineKeyboardButton(text="Далее", callback_data="1")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = await update.message.reply_text(text=text, reply_markup=reply_markup)
    context.chat_data["start_message"] = message
    User.safe_insert(update.effective_chat.id)

    # print(message.message_id)

    return 0


@async_logger
async def grade_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    return 1


@async_logger
async def get_tens_reply_markup():
    keyboard = []
    keyboard.append([
        InlineKeyboardButton(text="Β", callback_data="Β"),
        InlineKeyboardButton(text="Γ", callback_data="Γ"),
        InlineKeyboardButton(text="Δ", callback_data="Δ"),
        InlineKeyboardButton(text="Ε", callback_data="Ε"),
        InlineKeyboardButton(text="Ζ", callback_data="Ζ")
    ])
    keyboard.append([
        InlineKeyboardButton(text="Η", callback_data="Η"),
        InlineKeyboardButton(text="Θ", callback_data="Θ"),
        InlineKeyboardButton(text="Ι", callback_data="Ι"),
        InlineKeyboardButton(text="Κ", callback_data="Κ"),
        InlineKeyboardButton(text="Λ", callback_data="Λ"),
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


@async_logger
async def get_elevens_reply_markup():
    keyboard = []
    keyboard.append([
        InlineKeyboardButton(text="Μ", callback_data="Μ"),
        InlineKeyboardButton(text="Ξ", callback_data="Ξ"),
        InlineKeyboardButton(text="Ο", callback_data="Ο"),
        InlineKeyboardButton(text="Π", callback_data="Π"),
        InlineKeyboardButton(text="Ρ", callback_data="Ρ")
    ])
    keyboard.append([
        InlineKeyboardButton(text="Σ", callback_data="Σ"),
        InlineKeyboardButton(text="Τ", callback_data="Τ"),
        InlineKeyboardButton(text="Φ", callback_data="Φ"),
        InlineKeyboardButton(text="Χ", callback_data="Χ"),
        InlineKeyboardButton(text="Ψ", callback_data="Ψ"),
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


@async_logger
async def school_class_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = context.chat_data["start_message"]
    query = update.callback_query
    await query.answer()
    income = query.data
    context.chat_data["grade"] = income
    if income == "10 класс":
        reply_markup = await get_tens_reply_markup()
    if income == "11 класс":
        reply_markup = await get_elevens_reply_markup()

    text = get_telegram_message("class")
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )

    return 2


@async_logger
async def class_group_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    return 3


@async_logger
async def get_academic_group_reply_markup():
    keyboard = []
    keyboard.append([
        InlineKeyboardButton(text="1", callback_data="1 группа"),
        InlineKeyboardButton(text="2", callback_data="2 группа"),
        InlineKeyboardButton(text="3", callback_data="3 группа"),
        InlineKeyboardButton(text="4", callback_data="4 группа"),
        InlineKeyboardButton(text="5", callback_data="5 группа"),
        InlineKeyboardButton(text="6", callback_data="6 группа"),
    ])
    keyboard.append([
        InlineKeyboardButton(text="7", callback_data="7 группа"),
        InlineKeyboardButton(text="8", callback_data="8 группа"),
        InlineKeyboardButton(text="9", callback_data="9 группа"),
        InlineKeyboardButton(text="10", callback_data="10 группа"),
        InlineKeyboardButton(text="11", callback_data="11 группа"),
        InlineKeyboardButton(text="12", callback_data="12 группа"),
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


@async_logger
async def academic_group_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = context.chat_data["start_message"]
    query = update.callback_query
    await query.answer()
    income = query.data
    context.chat_data["class_group"] = income

    reply_markup = await get_academic_group_reply_markup()

    text = get_telegram_message("academic_group")
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )

    return 4


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
