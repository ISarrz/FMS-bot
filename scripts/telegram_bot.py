from modules.database import *
from modules.config import *
from modules.telegram_int.timetable.timetable import ConversationHandler_timetable
from modules.telegram_int.start.start import ConversationHandler_start
from modules.telegram_int.settings.settings import ConversationHandler_settings
from modules.logger.logger import async_logger, logger
from modules.config.paths import database_dump_path
from telegram import (
    Update
)
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    ContextTypes,
    CommandHandler
)


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
            try:
                if user.settings.notifications:
                    await context.bot.send_message(chat_id=user.telegram_id, text=notification.value)

            except Exception as e:
                pass

            notification.delete()


@async_logger
async def send_logs(context: CallbackContext):
    chat_id = get_config_field("logs_chat_id")
    for log in Log.all():
        await context.bot.send_message(chat_id=chat_id, text=log.value)
        log.delete()


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(text=str(chat_id))


@logger
def main():
    token = get_config_field('telegram_api_token')
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('info', info_message))
    application.add_handler(CommandHandler('get_chat_id', get_chat_id))
    application.add_handler(CommandHandler('get_database', get_database))
    application.add_handler(ConversationHandler_start, 1)
    application.add_handler(ConversationHandler_timetable, 2)
    application.add_handler(ConversationHandler_settings, 3)

    job_deque = application.job_queue
    job_deque.run_repeating(send_users_notifications, 20)
    job_deque.run_repeating(send_logs, 20)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
