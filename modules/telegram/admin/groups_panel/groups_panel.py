from telegram import (
    Update
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
from modules.telegram.admin.groups_panel.get_sheets import get_sheets, get_cur_sheet

ADMIN_CHAT_ID = get_config_field("admin_chat_id")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        await update.message.reply_text("Access denied")
        return ConversationHandler.END

    await update.message.reply_text("Access allowed")
    context.user_data['sheet'] = 0

    return 0


async def groups_overview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sheet = get_cur_sheet(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


ConversationHandler_groups_panel = ConversationHandler(
    entry_points=[CommandHandler('group_panel', start)],

    states={
        0: [CallbackQueryHandler(groups_overview)],
    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)
