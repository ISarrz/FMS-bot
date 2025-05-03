from modules.database_api import *
from modules.files_api import text_reader
from modules.files_api import *
from modules.time.dates import *
from modules.logger.logger import *
from modules.telegram_int.admin.admin_panel import ConversationHandler_admin_panel
from modules.telegram_int.settings.settings_menu import ConversationHandler_settings
from modules.telegram_int.timetable.timetable_menu import ConversationHandler_timetable
from modules.database_api.service.dumps import create_backup
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


async def send_logs(context: CallbackContext):
    logs_chat_id = get_config_field('logs_chat_id')
    logs = fetch_all_logs()
    for log in logs:
        await  context.bot.send_message(chat_id=logs_chat_id, text=log['value'])
        delete_logs_by_id(log['id'])


async def info_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = text_reader.read(telegram_info_message_path)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    telegram_id = update.effective_user.id
    if fetch_user_by_telegram_id(telegram_id):
        fetch_class_user_by_telegram_id(telegram_id)
    else:
        user_id = insert_user(telegram_id)
        insert_user_notifications_by_id(user_id)


async def get_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != get_config_field('admin_chat_id'):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No Access")
        return

    save_dump()
    dump_name = "database_dump.db"
    file_path = os.path.join(database_dumps_path, dump_name)

    with open(file_path, "rb") as sql_file:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=sql_file)


pass


# text = text_reader.read(telegram_info_message_path)
# await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
#
# telegram_id = update.effective_user.id
# if fetch_user_by_telegram_id(telegram_id):
#     fetch_class_user_by_telegram_id(telegram_id)
# else:
#     user_id = insert_user(telegram_id)
#     insert_user_notifications_by_id(user_id)


@async_logger
async def update_user_info(context: CallbackContext):
    print('user_update')
    users = fetch_all_class_users()

    for user in users:
        await update_user(context, user)


async def update_user(context, user):
    updated_dates = []
    for date in get_current_string_dates():
        user_groups = await get_user_groups(user)
        updated_groups = fetch_user_update_groups_by_date(user.id, date)
        updated_groups = [fetch_class_group_by_id(group['id']) for group in updated_groups]
        user_groups = [i for i in user_groups if i not in updated_groups]

        for group in user_groups:
            if fetch_image_id_by_date_and_group_id(date, group.id):
                updated_dates.append(date)
                insert_user_updates(user.id, date, group.id)

    updated_dates = list(set(updated_dates))

    notif_state = fetch_user_notifications(user.id)
    if updated_dates and notif_state['value']:
        text = 'Доступно расписание на: ' + ", ".join(updated_dates)
        await context.bot.send_message(chat_id=user.telegram_id, text=text)


async def get_user_groups(user):
    user_groups = fetch_user_groups_by_id(user.id)
    user_groups = [fetch_class_group_by_id(group['id']) for group in user_groups]
    return user_groups


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(text=str(chat_id))


def main():
    token = get_config_field('telegram_api_token')
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('start', info_message))
    application.add_handler(CommandHandler('get_chat_id', get_chat_id))
    application.add_handler(CommandHandler('get_database', get_database))
    application.add_handler(ConversationHandler_admin_panel, 1)
    application.add_handler(ConversationHandler_settings, 2)
    application.add_handler(ConversationHandler_timetable, 3)

    job_deque = application.job_queue
    job_deque.run_repeating(update_user_info, 30)
    job_deque.run_repeating(send_logs, 60)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
