from modules.config import get_telegram_message
from modules.database import Group, User
from modules.logger.logger import async_logger
from modules.statistics.statistics import get_statistics_field, set_statistics_field
from modules.telegram_int.start.sheets_generator import (get_ten_grade_sheet, get_eleven_grade_sheet,
                                                         get_eleven_grade_academic_groups_sheet,
                                                         get_ten_grade_academic_groups_sheet)

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


@async_logger
async def send_grade_menu(update: Update, context: CallbackContext):
    text = get_telegram_message("info")

    keyboard = []
    keyboard.append([InlineKeyboardButton(text="Далее", callback_data="1")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = await update.message.reply_text(text=text, reply_markup=reply_markup)
    context.chat_data["start_message"] = message


