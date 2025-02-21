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
from modules.telegram.admin.groups_panel.sheets import *
from modules.database_api import (
    DbGroup,
    insert_group,
    update_group_by_id,
    delete_group_by_id,
    insert_groups_relation,
    delete_groups_relation_by_groups_id,
    fetch_parent_by_id,
    fetch_child_by_id

)

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
    await update.message.reply_text(f"Groups №{context.chat_data['sheet'] + 1}", reply_markup=reply_markup)


async def update_overview(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    reply_markup = await get_reply_markup(update, context)

    await query.edit_message_text(
        text=f"Groups №{context.chat_data['sheet'] + 1}",
        reply_markup=reply_markup
    )


async def groups_overview(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            text=f"To add new group write:\n"
                 f"name:\n"
                 f"about:\n"
                 f"------------------\n"
                 f"To cancel write: cancel",
            reply_markup=reply_markup
        )

        return 1

    else:
        group = fetch_group_by_id(int(income))
        parent = fetch_parent_by_id(group['id'])
        parent = f"({parent['id']}) {parent['name']}" if parent else "None"
        child = fetch_child_by_id(group['id'])
        child = f"({child['id']}) {child['name']}" if child else "None"

        keyboard = [[]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"Group\n"
                 f"id: {group['id']}\n"
                 f"name: {group['name']}\n"
                 f"about: {group['about']}\n"
                 f"parent: {parent}\n"
                 f"child: {child}\n"
                 f"------------------\n"
                 f"To edit group write:\n"
                 f"id:\n"
                 f"name:\n"
                 f"about:\n"
                 f"------------------\n"
                 f"To delete group write: delete 'id'\n"
                 f"------------------\n"
                 f"To add groups relation write: add 'parent_id' 'child_id'\n"
                 f"------------------\n"
                 f"To delete groups relation write: del 'parent_id' 'child_id'\n"
                 f"------------------\n"
                 f"To cancel write: cancel\n"
            ,
            reply_markup=reply_markup
        )

        return 2


async def edit_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    income = update.message.text

    if "delete " in income:
        group_id = int(income.replace("delete ", ""))
        delete_group_by_id(group_id)

    elif "add " in income:
        income = income.replace("add ", "")
        parent_id, child_id = income.split(" ")
        insert_groups_relation(int(parent_id), int(child_id))

    elif "del " in income:
        income = income.replace("del ", "")
        parent_id, child_id = income.split(" ")
        delete_groups_relation_by_groups_id(int(parent_id), int(child_id))

    elif income != "cancel":
        group_id, group_name, group_about = income.split("\n")
        update_group_by_id(group_id=int(group_id), name=group_name, about=group_about)

    await send_overview(update, context)
    return 0


async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    income = update.message.text

    if income != "cancel":
        income = income.split("\n")
        name, about = income
        insert_group(name=name, about=about)

    await send_overview(update, context)

    return 0


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


ConversationHandler_groups_panel = ConversationHandler(
    entry_points=[CommandHandler('groups_panel', start)],

    states={
        0: [CallbackQueryHandler(groups_overview)],

        1: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_group)],
        2: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_group)]
    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)
