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

SETTINGS_CHOICE_HANDLER = 0
GROUPS_MENU_CHOICE_HANDLER = 1

from modules.telegram_int.settings_handler.sheets_generator import *
from modules.telegram_int.settings_handler.messages import *


@async_logger
async def start_settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    User.safe_insert(update.effective_chat.id)

    await send_settings_menu(update, context)

    return SETTINGS_CHOICE_HANDLER


@async_logger
async def settings_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data
    user = User(telegram_id=update.effective_chat.id)

    if income == "notifications":
        user.settings.switch_notifications_mode()
        await update_settings_menu(update, context)

        return SETTINGS_CHOICE_HANDLER

    if income == "mode":
        user.settings.switch_timetable_mode()
        await update_settings_menu(update, context)

        return SETTINGS_CHOICE_HANDLER

    if income == "groups":
        context.chat_data["settings_group"] = Group(name="ФМШ")
        context.chat_data["groups_sheet"] = 0
        await update_groups_menu(update, context)
        return GROUPS_MENU_CHOICE_HANDLER

    return ConversationHandler.END


@async_logger
async def groups_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        context.chat_data["groups_sheet"] = 0
        main_group = context.chat_data["settings_group"]
        if main_group.parent:
            context.chat_data["settings_group"] = main_group.parent
            await update_groups_menu(update, context)
            return GROUPS_MENU_CHOICE_HANDLER

        await update_settings_menu(update, context)
        return SETTINGS_CHOICE_HANDLER

    if income == LEFT_ARROW:
        sheets = get_groups_menu_sheets(update, context)
        context.chat_data["groups_sheet"] -= 1
        context.chat_data["groups_sheet"] += len(sheets)
        context.chat_data["groups_sheet"] %= len(sheets)

        await update_groups_menu(update, context)
        return GROUPS_MENU_CHOICE_HANDLER

    if income == RIGHT_ARROW:
        sheets = get_groups_menu_sheets(update, context)
        context.chat_data["groups_sheet"] += 1
        context.chat_data["groups_sheet"] %= len(sheets)

        await update_groups_menu(update, context)
        return GROUPS_MENU_CHOICE_HANDLER

    new_group = Group(id=int(income))
    if new_group.children:
        context.chat_data["groups_sheet"] = 0
        context.chat_data["settings_group"] = new_group

    else:
        user = User(telegram_id=update.effective_chat.id)
        if new_group.id in [ug.id for ug in user.groups]:
            user.delete_group(new_group)

            cur_group = new_group
            while cur_group.parent:
                children = [child.id for child in cur_group.parent.children]
                user_groups = [group.id for group in user.groups]
                if set(children) & set(user_groups):
                    break

                cur_group = cur_group.parent
                user.delete_group(cur_group)

        else:
            user.insert_group(new_group)

    await update_groups_menu(update, context)
    return GROUPS_MENU_CHOICE_HANDLER


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


ConversationHandler_settings = ConversationHandler(
    entry_points=[CommandHandler('settings', start_settings_handler)],

    states={
        SETTINGS_CHOICE_HANDLER: [CallbackQueryHandler(settings_menu_handler)],
        GROUPS_MENU_CHOICE_HANDLER: [CallbackQueryHandler(groups_menu_handler)],

    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)
