from modules.config import get_telegram_message
from modules.database import Group, User
from modules.logger.logger import async_logger
from modules.telegram_int.start_handler.sheets_generator import (
    get_ten_grade_sheet, get_eleven_grade_sheet,
    get_eleven_grade_academic_groups_sheet,
    get_ten_grade_academic_groups_sheet
)
from modules.data_updater.painter.updater import update_user
from modules.telegram_int.start_handler.messages import (
    update_grade_menu,
    send_start_menu,
    update_school_class_menu,
    update_class_group_menu,
    update_academic_group_menu,
    update_end_menu
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

GRADE_MENU_HANDLER = 0
SCHOOL_CLASS_HANDLER = 1
CLASS_GROUP_HANDLER = 2
ACADEMIC_GROUP_HANDLER = 3
END_HANDLER = 4


@async_logger
async def start_menu_handler(update: Update, context: CallbackContext):
    await send_start_menu(update, context)
    User.safe_insert(update.effective_chat.id)

    return GRADE_MENU_HANDLER


@async_logger
async def grade_menu_handler(update: Update, context: CallbackContext):
    await update_grade_menu(update, context)

    return SCHOOL_CLASS_HANDLER


@async_logger
async def school_class_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    grade = query.data
    context.chat_data["grade"] = grade

    await update_school_class_menu(update, context)

    return CLASS_GROUP_HANDLER


@async_logger
async def class_group_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    school_class = query.data
    context.chat_data["class"] = school_class

    await update_class_group_menu(update, context)

    return ACADEMIC_GROUP_HANDLER


@async_logger
async def academic_group_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    class_group = query.data
    context.chat_data["class_group"] = class_group

    await update_academic_group_menu(update, context)

    return END_HANDLER


@async_logger
async def end_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    academic_group = query.data
    context.chat_data["academic_group"] = academic_group

    await update_end_menu(update, context)

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

    update_user(user)

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


ConversationHandler_start = ConversationHandler(
    entry_points=[CommandHandler('start', start_menu_handler)],

    states={
        GRADE_MENU_HANDLER: [CallbackQueryHandler(grade_menu_handler)],
        SCHOOL_CLASS_HANDLER: [CallbackQueryHandler(school_class_menu_handler)],
        CLASS_GROUP_HANDLER: [CallbackQueryHandler(class_group_menu_handler)],
        ACADEMIC_GROUP_HANDLER: [CallbackQueryHandler(academic_group_menu_handler)],
        END_HANDLER: [CallbackQueryHandler(end_handler)],
    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)
