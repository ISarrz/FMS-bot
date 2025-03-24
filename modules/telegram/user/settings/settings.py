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
from modules.telegram.user.settings.sheets import *

from modules.database_api import *


# from modules.database.group import Group
# from modules.telegram_modules import functions as fnc
# from modules.telegram_modules import custom_filters
# from modules.database.user import User
# from modules.database.database import db
# from modules.telegram_modules.settings import menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    db_response = fetch_user_by_telegram_id(telegram_id)
    if not db_response:
        insert_user(telegram_id)

    await send_main_menu(update, context)

    return 0


async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = get_main_menu(update, context)

    await update.message.reply_text(text="Настройки", reply_markup=reply_markup)


async def update_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    reply_markup = get_main_menu(update, context)

    await query.edit_message_text(
        text="Настройки", reply_markup=reply_markup
    )


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data

    telegram_id = update.message.from_user.id
    user = fetch_user_by_telegram_id(telegram_id)

    sheets = get_user_groups_sheets(user['id'])

    if income == "<-":
        context.chat_data['sheet'] += 1
        context.chat_data['sheet'] %= len(sheets)

        await update_main_menu(update, context, query)

        return 0

    elif income == "->":
        context.chat_data['sheet'] -= 1
        context.chat_data['sheet'] += len(sheets)
        context.chat_data['sheet'] %= len(sheets)

        await update_main_menu(update, context, query)

        return 0

    elif income == "+":
        pass

    else:
        group = fetch_group_by_id(int(income))
        db_group = DbGroup(id=group['id'], name=group['name'], about=group['about'])
        parents = fetch_groups_sequence(db_group.id)
        if len(parents) > 1:
            text = f"{db_group.name} " + "; ".join(i['name'] for i in parents[1:])

        else:
            text = db_group.name

        keyboard = [[InlineKeyboardButton(text='✔', callback_data='✔'),
                     InlineKeyboardButton(text='❌', callback_data='❌')
                     ]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"Удалить группу {text}?",
            reply_markup=reply_markup
        )


async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    query = update.callback_query
    await query.answer()
    income = query.data


async def delete_group(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    query = update.callback_query
    await query.answer()
    income = query.data


async def settings_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data

    # if income == 'notification':
    #     user = User(db, telegram_id=update.effective_user.id)
    #     notif_state = user.settings['notification']
    #     user.settings = {'notification': not notif_state}
    #
    #     text, reply_markup = menu.get_main_menu(update, context)
    #     await query.edit_message_text(text=text, reply_markup=reply_markup)
    #
    #     return 0

    if income == 'group':
        reply_markup = get_group_menu(update, context)

        await query.edit_message_text(text=f"Группы №{context.user_data['sheet'] + 1}", reply_markup=reply_markup)

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
