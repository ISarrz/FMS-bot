from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)
from modules.telegram_int.admin.symbols import *
from modules.files_api.config import *
from modules.telegram_int.admin.events_menu import (
    update_events_groups_mode_menu,
    update_add_event_menu,
    update_dates_menu,
    update_events_events_mode_menu,
    update_edit_event_menu,
    get_dates_menu_sheets,
    get_events_events_mode_menu_sheets,
    get_events_groups_mode_menu_sheets,
    add_event,
    edit_event,
    edit_event_menu_response, delete_event_response

)
from modules.telegram_int.admin.groups_menu import *
from modules.telegram_int.admin.main_menu import *

ADMIN_CHAT_ID = get_config_field("admin_chat_id")


@async_logger
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        await update.message.reply_text("Access denied")
        return ConversationHandler.END

    await send_main_menu(update, context)
    return 0


@async_logger
async def main_menu_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == "events":
        await update_dates_menu(update, context, query)
        return 1

    if income == "groups":
        await update_groups_menu(update, context, query)
        return 2


@async_logger
async def groups_menu_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        parent_group = fetch_class_parent_by_id(context.chat_data['group'])
        context.chat_data['sheet'] = 0
        if parent_group:
            context.chat_data['group'] = parent_group.id
            await update_groups_menu(update, context, query)
            return 2

        await update_main_menu(update, context, query)
        return 0

    if income == ADD:
        await update_add_group_menu(update, context, query)
        return 3

    if income == EDIT:
        await update_edit_group_menu(update, context, query)
        return 4

    if income == LEFT_ARROW:
        sheets = await get_groups_menu_sheets(update, context)
        context.chat_data['sheet'] -= 1
        context.chat_data['sheet'] += len(sheets)
        context.chat_data['sheet'] %= len(sheets)

        await update_groups_menu(update, context, query)
        return 2

    if income == RIGHT_ARROW:
        sheets = await get_groups_menu_sheets(update, context)
        context.chat_data['sheet'] += 1
        context.chat_data['sheet'] %= len(sheets)
        await update_groups_menu(update, context, query)
        return 2

    context.chat_data['group'] = int(income)
    context.chat_data['sheet'] = 0
    await update_groups_menu(update, context, query)
    return 2


@async_logger
async def dates_menu_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == LEFT_ARROW:
        sheets = await get_dates_menu_sheets(update, context)
        context.chat_data['sheet'] -= 1
        context.chat_data['sheet'] += len(sheets)
        context.chat_data['sheet'] %= len(sheets)
        await update_dates_menu(update, context, query)

        return 1

    elif income == RIGHT_ARROW:
        sheets = await get_dates_menu_sheets(update, context)
        context.chat_data['sheet'] += 1
        context.chat_data['sheet'] %= len(sheets)
        await update_dates_menu(update, context, query)

        return 1

    elif income == BACK_ARROW:
        await update_main_menu(update, context, query)

        return 0

    context.chat_data['date'] = income
    context.chat_data['mode'] = 'groups'
    await update_events_groups_mode_menu(update, context, query)
    return 7


@async_logger
async def events_menu_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW and context.chat_data['mode'] == 'groups':
        parent_group = fetch_class_parent_by_id(context.chat_data['group'])
        context.chat_data['sheet'] = 0
        if parent_group:
            context.chat_data['group'] = parent_group.id
            await update_events_groups_mode_menu(update, context, query)
            return 7

        await update_dates_menu(update, context, query)
        return 1

    if income == ADD and context.chat_data['mode'] == 'events':
        context.chat_data['sheet'] = 0
        await update_add_event_menu(update, context, query)
        return 8

    if income == LEFT_ARROW and context.chat_data['mode'] == 'groups':
        sheets = await get_events_groups_mode_menu_sheets(update, context)
        context.chat_data['sheet'] -= 1
        context.chat_data['sheet'] += len(sheets)
        context.chat_data['sheet'] %= len(sheets)

        await update_events_groups_mode_menu(update, context, query)
        return 7

    if income == RIGHT_ARROW and context.chat_data['mode'] == 'groups':
        sheets = await get_events_groups_mode_menu_sheets(update, context)
        context.chat_data['sheet'] += 1
        context.chat_data['sheet'] %= len(sheets)
        await update_events_groups_mode_menu(update, context, query)
        return 7

    if income == LEFT_ARROW and context.chat_data['mode'] == 'events':
        sheets = await get_events_events_mode_menu_sheets(update, context)
        context.chat_data['sheet'] -= 1
        context.chat_data['sheet'] += len(sheets)
        context.chat_data['sheet'] %= len(sheets)

        await update_events_events_mode_menu(update, context, query)
        return 7

    if income == RIGHT_ARROW and context.chat_data['mode'] == 'events':
        sheets = await get_events_events_mode_menu_sheets(update, context)
        context.chat_data['sheet'] += 1
        context.chat_data['sheet'] %= len(sheets)
        await update_events_events_mode_menu(update, context, query)
        return 7

    if income == 'events':
        context.chat_data['mode'] = 'events'
        context.chat_data['sheet'] = 0
        await update_events_events_mode_menu(update, context, query)
        return 7

    if income == 'groups':
        context.chat_data['mode'] = 'groups'
        context.chat_data['sheet'] = 0
        await update_events_groups_mode_menu(update, context, query)
        return 7

    if context.chat_data['mode'] == 'events':
        # event edit menu
        context.chat_data['event'] = int(income)
        await update_edit_event_menu(update, context, query)
        return 9

    if context.chat_data['mode'] == 'groups':
        # group mode
        context.chat_data['group'] = int(income)
        context.chat_data['sheet'] = 0
        await update_events_groups_mode_menu(update, context, query)
        return 7


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


ConversationHandler_admin_panel = ConversationHandler(
    entry_points=[CommandHandler('admin_panel', start)],

    states={
        0: [CallbackQueryHandler(main_menu_response)],
        1: [CallbackQueryHandler(dates_menu_response)],
        2: [CallbackQueryHandler(groups_menu_response)],
        3: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_group)],
        4: [CallbackQueryHandler(edit_group_menu_response)],
        5: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_group)],
        6: [CallbackQueryHandler(delete_group_response)],
        7: [CallbackQueryHandler(events_menu_response)],
        8: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_event)],
        9: [CallbackQueryHandler(edit_event_menu_response)],
        10: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_event)],
        11: [CallbackQueryHandler(delete_event_response)],
    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)
