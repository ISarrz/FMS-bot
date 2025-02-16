import os
from modules.files_api import get_config_field
from telegram import *
from telegram.ext import *
from modules.telegram import ConversationHandler_groups_panel
from modules.telegram import ConversationHandler_events_panel


# async def help_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     text = fnc.get_message('help', 'help.txt')
#     await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
#

async def start_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "TEST"
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
    application.add_handler(ConversationHandler_groups_panel, 1)
    application.add_handler(ConversationHandler_events_panel, 2)
    # application.add_handler(settings.ConversationHandler_settings, 2)
    # application.add_handler(today.ConversationHandler_today, 3)
    # application.add_handler(timetable.ConversationHandler_timetable, 4)
    # application.add_handler(timetable, 5)

    # job_deque = application.job_queue
    # job_deque.run_repeating(send_report, 1 * 60, chat_id=files_worker.get_constant('twink_develop_chat_id'))
    # job_deque.run_repeating(send_new_timetable, 10)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
