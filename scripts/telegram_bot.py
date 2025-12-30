from modules.database import *
from modules.config import *
from modules.config.paths import archive
from modules.telegram_int.timetable.timetable import ConversationHandler_timetable
from modules.telegram_int.start.start import ConversationHandler_start
from modules.telegram_int.settings.settings import ConversationHandler_settings
from modules.logger.logger import async_logger, logger
from modules.config.paths import database_dump_path
from modules.statistics import statistics
from io import BytesIO
from datetime import datetime
from telegram import (
    Update
)
import sqlite3
from modules.config.paths import database_path
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    ContextTypes,
    CommandHandler
)


async def get_database(update: Update, context: CallbackContext):
    pass
    # if update.effective_chat.id != get_config_field('admin_chat_id'):
    #     await context.bot.send_message(chat_id=update.effective_chat.id, text="No Access")
    #     return
    #
    # # with sqlite3.connect(database_path) as src_conn:
    # #     with sqlite3.connect(database_dump_path) as dest_conn:
    # #         src_conn.backup(dest_conn, pages=0, progress=None)
    #
    #
    # with open(archive, "rb") as sql_file:
    #     await context.bot.send_document(chat_id=update.effective_chat.id, document=sql_file)


@async_logger
async def send_notification(update: Update, context: CallbackContext):
    count = statistics.get_statistics_field("sent_notifications_count")
    if update.effective_chat.id != get_config_field('admin_chat_id'):
        pass
        await update.message.reply_text("Access denied")
        return
    # context.args содержит список аргументов после команды
    if context.args:
        text = " ".join(context.args)  # собираем строку
        await update.message.reply_text(f"Вы написали: {text}")
        for user in User.all():
            user.insert_notification(text)
    else:
        await update.message.reply_text("❌ Вы не передали строку.\nПример: /echo Привет!")




@async_logger
async def send_users_notifications(context: CallbackContext):
    count = statistics.get_statistics_field("sent_notifications_count")
    for user in User.all():
        for notification in user.notifications:
            try:
                if user.settings.notifications:
                    await context.bot.send_message(chat_id=user.telegram_id, text=notification.value)
                    count += 1

            except Exception as e:
                pass

            notification.delete()

    statistics.set_statistics_field("sent_notifications_count", count)


@async_logger
async def send_statistics(context: CallbackContext):
    data = statistics.get_statistics()
    text = ""
    for key in data.keys():
        text += f"{key}: {data[key]}\n"

    chat_id = get_config_field('admin_chat_id')

    await context.bot.send_message(chat_id=chat_id, text=text)


@async_logger
async def day_statistics(context: CallbackContext):
    if not context.bot_data.get("sent_statistics"):
        context.bot_data["sent_statistics"] = False

    if datetime.now().hour == 12 and not context.bot_data["sent_statistics"]:
        statistics.update_statistics()
        context.bot_data["sent_statistics"] = True
        await send_statistics(context)
        statistics.reset_statistics()

    if datetime.now().hour != 12:
        context.bot_data["sent_statistics"] = False


@async_logger
async def get_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    statistics.update_statistics()
    await send_statistics(context)


@async_logger
async def send_logs(context: CallbackContext):
    chat_id = get_config_field("logs_chat_id")
    for log in Log.all():
        bio = BytesIO(log.value.encode("utf-8"))
        bio.name = "log.txt"
        if len(log.value) > 4096:
            await context.bot.send_document(chat_id=chat_id, document=bio)
        else:
            await context.bot.send_message(chat_id=chat_id, text=log.value)
        log.delete()


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(text=str(chat_id))



def main():
    statistics.reset_statistics()

    token = get_config_field('telegram_api_token')
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('get_chat_id', get_chat_id))
    application.add_handler(CommandHandler('get_database', get_database))
    application.add_handler(CommandHandler('send_notification', send_notification))
    application.add_handler(CommandHandler('get_statistics', get_statistics))
    application.add_handler(ConversationHandler_start, 1)
    application.add_handler(ConversationHandler_timetable, 2)
    application.add_handler(ConversationHandler_settings, 3)

    job_deque = application.job_queue
    job_deque.run_repeating(send_users_notifications, 20)
    job_deque.run_repeating(send_logs, 20)
    job_deque.run_repeating(day_statistics, 20)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
