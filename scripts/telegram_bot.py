from modules.database import *
from modules.config import *

from modules.telegram_int.timetable_handler.handlers import ConversationHandler_timetable
from modules.telegram_int.start_handler.handlers import ConversationHandler_start
from modules.telegram_int.settings_handler.handlers import ConversationHandler_settings
from modules.logger.logger import async_logger, logger

from modules.statistics.statistics import statistic
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


async def save_database(update: Update, context: CallbackContext):
    if update.effective_chat.id != get_config_field('admin_chat_id'):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No Access")
        return

    if DB.make_backup() == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id,text="Успешно")

    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ошибка")

@async_logger
async def send_notification(update: Update, context: CallbackContext):
    if update.effective_chat.id != get_config_field('admin_chat_id'):
        await update.message.reply_text("Доступ запрещен")
        return

    if context.args:
        text = " ".join(context.args)
        await update.message.reply_text(f"Вы написали: {text}")
        for user in User.all():
            user.insert_notification(text)
    else:
        await update.message.reply_text("Строка пуста")


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
async def day_statistics(context: CallbackContext):
    if not context.bot_data.get("sent_statistics"):
        context.bot_data["sent_statistics"] = False

    if datetime.now().hour == 12 and not statistic.flag:
        statistic.flag = True
        statistic.reset()
        text = str(statistic)
        chat_id = get_config_field('admin_chat_id')
        await context.bot.send_message(chat_id=chat_id, text=text)

    if datetime.now().hour != 12:
        statistic.flag = False
        context.bot_data["sent_statistics"] = False


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


async def get_chat_id(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    await update.message.reply_text(text=str(chat_id))


def main():
    statistic.reset()
    token = get_config_field('telegram_api_token')
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('get_chat_id', get_chat_id))
    application.add_handler(CommandHandler('save_database', save_database))
    application.add_handler(CommandHandler('send_notification', send_notification))
    application.add_handler(ConversationHandler_start, 1)
    application.add_handler(ConversationHandler_timetable, 2)
    application.add_handler(ConversationHandler_settings, 3)

    job_deque = application.job_queue
    job_deque.run_repeating(send_users_notifications, 60)
    job_deque.run_repeating(send_logs, 20)
    job_deque.run_repeating(day_statistics, 60)
    #
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
