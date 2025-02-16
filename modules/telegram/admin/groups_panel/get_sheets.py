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
from modules.database_api import (
    fetch_all_groups,
    fetch_group_by_id
)


def get_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    groups = [fetch_group_by_id(group["id"]) for group in fetch_all_groups()]
    sheet_size = 5
    sheets = [[]]
    while groups:
        if len(sheets[-1]) > sheet_size:
            sheets.append([])

        sheets[-1].append(groups.pop())

    return sheets


def get_cur_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return get_sheets(update, context)[context.user_data['sheet']]
