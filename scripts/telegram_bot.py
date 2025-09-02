from modules.database import *
from modules.config import *
# from modules.time.dates import *
# from modules.logger.logger import *
# from modules.telegram_int.admin.admin_panel import ConversationHandler_admin_panel
# from modules.telegram_int.settings.settings_menu import ConversationHandler_settings
from modules.telegram_int.timetable.timetable import ConversationHandler_timetable
from modules.telegram_int.start.start import ConversationHandler_start
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ApplicationBuilder
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,

    MessageHandler,
    filters,

)
from telegram.ext import (
    CallbackContext,
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from modules.logger.logger import async_logger
from modules.config.paths import database_dump_path


async def get_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != get_config_field('admin_chat_id'):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No Access")
        return

    DB.save_backup()

    with open(database_dump_path, "rb") as sql_file:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=sql_file)


@async_logger
async def info_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_telegram_message("info")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


@async_logger
async def send_users_notifications(context: CallbackContext):
    for user in User.all():
        for notification in user.notifications:
            await context.bot.send_message(chat_id=user.telegram_id, text=notification.value)
            notification.delete()


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(text=str(chat_id))


from modules.logger.logger import async_logger, logger


@logger
def main():
    token = get_config_field('telegram_api_token')
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('info', info_message))
    application.add_handler(CommandHandler('get_chat_id', get_chat_id))
    application.add_handler(CommandHandler('get_database', get_database))
    application.add_handler(ConversationHandler_start, 1)
    application.add_handler(ConversationHandler_timetable, 2)

    job_deque = application.job_queue
    job_deque.run_repeating(send_users_notifications, 60)
    # job_deque.run_repeating(send_logs, 20)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
