from telegram import (
    Update
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from modules.database.group import Group
from modules.telegram_modules import functions as fnc
from modules.telegram_modules import custom_filters
from modules.database.user import User
from modules.database.database import db
from modules.telegram_modules.settings import menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not User.in_database(db, telegram_id=update.effective_user.id):
        await update.message.reply_text(fnc.get_message('settings', 'user_authentication_error.txt'))
        return ConversationHandler.END

    context.user_data['sheet'] = 0

    text, reply_markup = menu.get_main_menu(update, context)

    await update.message.reply_text(text=text, reply_markup=reply_markup)

    return 0


async def settings_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == 'notification':
        user = User(db, telegram_id=update.effective_user.id)
        notif_state = user.settings['notification']
        user.settings = {'notification': not notif_state}

        text, reply_markup = menu.get_main_menu(update, context)
        await query.edit_message_text( text=text, reply_markup=reply_markup)

        return 0

    if income == 'group':
        text, reply_markup = menu.get_group_menu(update, context)

        await query.edit_message_text(text=text, reply_markup=reply_markup)

        return 1


async def group_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data
    if income == 'left':
        context.user_data['sheet'] -= 1

        text, reply_markup = menu.get_group_menu(update, context)
        await query.edit_message_text(text=text, reply_markup=reply_markup)

        return 1

    if income == 'right':
        context.user_data['sheet'] += 1

        text, reply_markup = menu.get_group_menu(update, context)
        await query.edit_message_text(text=text, reply_markup=reply_markup)

        return 1

    if income == 'back':
        text, reply_markup = menu.get_main_menu(update, context)
        await query.edit_message_text(text=text, reply_markup=reply_markup)

        return 0

    if ', ' in income:
        income = income.split(', ')
        income = int(income[0]), bool(int(income[1]))
        # add or delete user group
        if income[1]:
            # delete
            group = Group(db, id=income[0])
            user = User(db, telegram_id=update.effective_user.id)
            user.delete_group(group)

        else:
            # add
            group = Group(db, id=income[0])
            user = User(db, telegram_id=update.effective_user.id)
            user.add_group(group)

        text, reply_markup = menu.get_group_menu(update, context)

        await query.edit_message_text(text=text, reply_markup=reply_markup)
        return 1


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


ConversationHandler_settings = ConversationHandler(
    entry_points=[CommandHandler('settings', start, filters=custom_filters.private)],

    states={
        0: [CallbackQueryHandler(settings_choice)],
        1: [CallbackQueryHandler(group_choice)],

    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)
