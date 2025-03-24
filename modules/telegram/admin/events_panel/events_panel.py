from telegram import (
    Update, InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from modules.files_api import get_config_field
from modules.telegram.admin.events_panel.sheets import *
from modules.database_api import *

ADMIN_CHAT_ID = get_config_field("admin_chat_id")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        await update.message.reply_text("Access denied")
        return ConversationHandler.END

    context.chat_data['sheet'] = 0
    await send_overview(update, context)
    return 0


async def send_overview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = await get_reply_markup(update, context)
    await update.message.reply_text(f"Events №{context.chat_data['sheet'] + 1}", reply_markup=reply_markup)


async def update_overview(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    reply_markup = await get_reply_markup(update, context)

    await query.edit_message_text(
        text=f"Event №{context.chat_data['sheet'] + 1}",
        reply_markup=reply_markup
    )


async def events_overview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data
    sheets = await get_sheets(update, context)

    if income == "->":
        context.chat_data['sheet'] += 1
        context.chat_data['sheet'] %= len(sheets)

        await update_overview(update, context, query)

        return 0

    elif income == "<-":
        context.chat_data['sheet'] -= 1
        context.chat_data['sheet'] += len(sheets)
        context.chat_data['sheet'] %= len(sheets)

        await update_overview(update, context, query)

        return 0

    elif income == "+":
        keyboard = [[]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"To add new event write:\n"
                 f"name:\n"
                 f"about:\n"
                 f"date:\n"
                 f"start:\n"
                 f"end:\n"
                 f"owner:\n"
                 f"place:\n"
                 f"------------------\n"
                 f"To cancel write: cancel",
            reply_markup=reply_markup
        )

        return 1

    else:
        event = fetch_event_by_id((int(income)))
        groups = fetch_event_groups_by_id(event['id'])
        if not groups:
            groups = "None"

        else:
            groups = ', '.join([f"({group['id']}) {group['name']}" for group in groups])

        keyboard = [[]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"Event\n"
                 f"id: {event['id']}\n"
                 f"name: {event['name']}\n"
                 f"about: {event['about']}\n"
                 f"date: {event['date']}\n"
                 f"start: {event['start']}\n"
                 f"end: {event['end']}\n"
                 f"owner: {event['owner']}\n"
                 f"place: {event['place']}\n"
                 f"groups: {groups}\n"
                 f"------------------\n"
                 f"To edit event write:\n"
                 f"id: \n"
                 f"name: \n"
                 f"about: \n"
                 f"date: \n"
                 f"start: \n"
                 f"end: \n"
                 f"owner: \n"
                 f"place: \n"
                 f"------------------\n"
                 f"To delete event write: delete 'id'\n"
                 f"------------------\n"
                 f"To add group event write: add 'group_id' 'event_id'\n"
                 f"------------------\n"
                 f"To delete group event write: del 'group_id' 'event_id'\n"
                 f"------------------\n"
                 f"To cancel write: cancel\n"
            ,
            reply_markup=reply_markup
        )

        return 2


async def edit_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    income = update.message.text

    if "delete " in income:
        event_id = int(income.replace("delete ", ""))
        delete_event_by_id(event_id)

    elif "add " in income:
        income = income.replace("add ", "")
        group_id, event_id = income.split(" ")
        insert_group_event(int(group_id), int(event_id))

    elif "del " in income:
        income = income.replace("del ", "")
        group_id, event_id = income.split(" ")
        delete_group_event_by_group_and_event_id(int(group_id), int(event_id))

    elif income != "cancel":
        event_id, name, about, date, start, end, owner, place = income.split("\n")
        update_event_by_id(int(event_id), name, about, date, start, end, owner, place)

    await send_overview(update, context)
    return 0


async def add_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    income = update.message.text

    if income != "cancel":
        income = income.split("\n")
        name, about, date, start, end, owner, place = income
        insert_event(name, about, date, start, end, owner, place)

    await send_overview(update, context)

    return 0


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('end')
    return ConversationHandler.END


ConversationHandler_events_panel = ConversationHandler(
    entry_points=[CommandHandler('events_panel', start)],

    states={
        0: [CallbackQueryHandler(events_overview)],

        1: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_event)],
        2: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_event)]
    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)
