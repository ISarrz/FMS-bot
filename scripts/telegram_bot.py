import os
from modules.files_api import get_config_field
from telegram import *
from telegram.ext import *
from modules.telegram import ConversationHandler_admin_panel
from modules.telegram.settings.settings_menu import ConversationHandler_settings
from modules.telegram.timetable.timetable_menu import ConversationHandler_timetable
from modules.database_api import *


# async def help_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     text = fnc.get_message('help', 'help.txt')
#     await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
#

async def start_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "TEST"
    telegram_id = update.effective_user.id
    if fetch_user_by_telegram_id(telegram_id):
        fetch_class_user_by_telegram_id(telegram_id)
    else:
        user_id = insert_user(telegram_id)
        insert_user_notifications_by_id(user_id)

    await update.message.reply_text(text=text)


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(text=str(chat_id))


# write sending new timetable


def main():
    token = get_config_field('telegram_api_token')
    application = ApplicationBuilder().token(token).build()

    # application.add_handler(CommandHandler('help', help_message))
    application.add_handler(CommandHandler('start', start_message))
    application.add_handler(CommandHandler('get_chat_id', get_chat_id))
    # application.add_handler(CommandHandler('today', today.today_message))
    #
    # application.add_handler(start.ConversationHandler_start, 1)
    # application.add_handler(ConversationHandler_groups_panel, 1)
    application.add_handler(ConversationHandler_admin_panel, 1)
    application.add_handler(ConversationHandler_settings, 2)
    application.add_handler(ConversationHandler_timetable, 3)

    # application.add_handler(ConversationHandler_events_panel, 2)
    # application.add_handler(settings.ConversationHandler_settings, 2)
    # application.add_handler(today.ConversationHandler_today, 3)
    # application.add_handler(timetable.ConversationHandler_timetable, 4)
    # application.add_handler(timetable, 5)

    async def callback(context: CallbackContext):
        job = context.job

        await context.bot.send_message(job.chat_id, text=f"OK")

    # job_deque = application.job_queue
    # job_deque.run_repeating(callback, 5, chat_id=get_config_field('admin_chat_id'))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
