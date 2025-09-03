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

TICK = "✓︎"
CROSS = "⨯"


def get_settings(user: User):
    keyboard = []

    text = f"Уведомления {TICK if user.settings.notifications else CROSS}"
    keyboard.append([InlineKeyboardButton(text=text, callback_data="notifications")])
    text = "Режим: изображение" if user.settings.mode == "image" else "Режим: текст"
    keyboard.append([InlineKeyboardButton(text=text, callback_data="mode")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


@async_logger
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    User.safe_insert(update.effective_chat.id)


    sheet = get_settings(User(telegram_id=update.effective_chat.id))

    message = await update.message.reply_text(text="Настройки", reply_markup=sheet)

    context.chat_data['settings_message'] = message

    return 0


@async_logger
async def update_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data
    user = User(telegram_id=update.effective_chat.id)
    if income == "notifications":
        user.settings.notifications = not user.settings.notifications

    if income == "mode":
        user.settings.mode = "image" if user.settings.mode == "text" else "text"

    message = context.chat_data['settings_message']

    reply_markup = get_settings(user)
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text="Настройки",
        reply_markup=reply_markup
    )
    return 0


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


ConversationHandler_settings = ConversationHandler(
    entry_points=[CommandHandler('settings', start)],

    states={
        0: [CallbackQueryHandler(update_settings)],

    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)
