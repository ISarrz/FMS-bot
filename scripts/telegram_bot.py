import sys
import traceback

from modules.database import *
from modules.config import *
from datetime import time
from modules.telegram_int.timetable_handler.handlers import ConversationHandler_timetable
from modules.telegram_int.start_handler.handlers import ConversationHandler_start
from modules.telegram_int.settings_handler.handlers import ConversationHandler_settings
from modules.logger.logger import async_logger

from modules.statistics.statistics import statistic
from io import BytesIO
from datetime import datetime
from telegram import (
    Update
)
from telegram.error import RetryAfter, TimedOut, NetworkError

from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler
)


async def save_database(update: Update, context: CallbackContext):
    if update.effective_chat.id != get_config_field('admin_chat_id'):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No Access")
        return

    if DB.make_backup():
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Успешно")

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
    text = str(statistic)
    chat_id = get_config_field('admin_chat_id')
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    statistic.reset()



async def get_statistics(update: Update, context: CallbackContext):
    text = str(statistic)
    chat_id = get_config_field('admin_chat_id')
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")


async def send_logs(context: CallbackContext):
    # Не оборачивать в @async_logger: при сбое отправки traceback попадёт в Log,
    # который тут же повторно попытается улететь — это и вызывало flood-лавину.
    chat_id = get_config_field("logs_chat_id")
    logs = Log.all()
    if not logs:
        return

    BATCH_LIMIT = 100
    batch = logs[:BATCH_LIMIT]

    try:
        if len(batch) == 1 and len(batch[0].value) <= 4096:
            await context.bot.send_message(chat_id=chat_id, text=batch[0].value)
        else:
            combined = "\n\n---\n\n".join(log.value for log in batch)
            bio = BytesIO(combined.encode("utf-8"))
            bio.name = f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            await context.bot.send_document(chat_id=chat_id, document=bio)
    except (RetryAfter, TimedOut, NetworkError):
        return
    except Exception:
        traceback.print_exc(file=sys.stderr)
        return

    for log in batch:
        log.delete()


async def get_chat_id(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    await update.message.reply_text(text=str(chat_id))


def main():
    statistic.reset()
    token = get_config_field('telegram_api_token')
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('get_chat_id', get_chat_id))
    # application.add_handler(CommandHandler('get_statistics', get_statistics))
    # application.add_handler(CommandHandler('save_database', save_database))
    # application.add_handler(CommandHandler('send_notification', send_notification))
    application.add_handler(ConversationHandler_start, 1)
    # application.add_handler(ConversationHandler_timetable, 2)
    # application.add_handler(ConversationHandler_settings, 3)

    # job_deque = application.job_queue
    # job_deque.run_repeating(send_users_notifications, 60)
    # job_deque.run_repeating(send_logs, 20)
    # job_deque.run_daily(day_statistics, time(hour=9, minute=0))
    #
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
