import json

from telegram import Update
from telegram.ext import (
    CallbackContext
)
from modules.config.paths import telegram_data_path

LEFT_ARROW = "←"
RIGHT_ARROW = "→"
BACK_ARROW = "↵"
ADD = "+"
EDIT = "edit"
DELETE = "❌"
SUBMIT = "✓︎"
CANCEL = "⨯"
TICK = "✓︎"
CROSS = "⨯"


def set_last_message_id(telegram_id, message_id):
    with open(telegram_data_path, "w") as f:
        data = {f"{telegram_id} last_message_id": message_id}
        json.dump(data, f)


def get_last_message_id(telegram_id):
    with open(telegram_data_path, "r") as f:
        data = json.load(f)
        return data[f"{telegram_id} last_message_id"]

async def clear_last_message(update:Update, context: CallbackContext):
    try:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=get_last_message_id(update.effective_chat.id)
        )

    except Exception:
        pass