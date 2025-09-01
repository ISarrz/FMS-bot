from modules.database import *
from modules.config import *
# from modules.time.dates import *
# from modules.logger.logger import *
# from modules.telegram_int.admin.admin_panel import ConversationHandler_admin_panel
# from modules.telegram_int.settings.settings_menu import ConversationHandler_settings
# from modules.telegram_int.timetable.timetable_menu import ConversationHandler_timetable
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



async def info_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_telegram_message("info")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    # telegram_id = update.effective_user.id
    # if fetch_user_by_telegram_id(telegram_id):
    #     fetch_class_user_by_telegram_id(telegram_id)
    # else:
    #     user_id = insert_user(telegram_id)
    #     insert_user_notifications_by_id(user_id)




async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(text=str(chat_id))


def main():
    token = get_config_field('telegram_api_token')
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('info', info_message))
    application.add_handler(CommandHandler('get_chat_id', get_chat_id))
    application.add_handler(ConversationHandler_start, 1)
    # application.add_handler(ConversationHandler_admin_panel, 1)
    # application.add_handler(ConversationHandler_settings, 2)
    # application.add_handler(ConversationHandler_timetable, 3)

    job_deque = application.job_queue
    # job_deque.run_repeating(update_user_info, 60)
    # job_deque.run_repeating(send_logs, 20)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
