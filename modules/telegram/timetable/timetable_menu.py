from telegram import (
    Update, InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from modules.files_api import get_config_field
from modules.database_api import (
    DbGroup,
    insert_group,
    update_group_by_id,
    delete_group_by_id,
    insert_groups_relation,
    delete_groups_relation_by_groups_id,
    fetch_parent_by_id,
    fetch_child_by_id

)
from modules.telegram.admin.events_menu import *
from modules.telegram.admin.main_menu import *
from modules.telegram.admin.groups_menu import *

ADMIN_CHAT_ID = get_config_field("admin_chat_id")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    if not fetch_user_by_telegram_id(telegram_id):
        user_id = insert_user(telegram_id)
        insert_user_notifications_by_id(user_id)

    context.chat_data['sheet'] = 0
    await send_timetable_dates_menu(update, context)
    return 0


async def send_timetable_dates_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sheet = await get_timetable_dates_menu_sheet(update, context)

    await update.message.reply_text(text=sheet.get('text'), reply_markup=sheet.get('reply_markup'))


async def update_timetable_dates_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    sheet = await get_timetable_dates_menu_sheet(update, context)

    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def get_timetable_dates_menu_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cur_sheet = int(context.chat_data.get('sheet'))
    sheets = await get_timetable_dates_menu_sheets(update, context)
    if sheets:
        return sheets[cur_sheet]

    return {'text': 'Расписания нет', 'reply_markup': None}


async def get_timetable_dates_menu_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = fetch_class_user_by_telegram_id(telegram_id)
    sheets = [{'text': '', 'reply_markup': None}, {'text': '', 'reply_markup': None}]

    weekdays = get_current_week_string_weekdays()
    for ind, date in enumerate(get_current_week_string_days()):
        # date as callback
        if not user_have_events_on_date(user.id, date):
            continue

        sheets[0]['reply_markup'] = [InlineKeyboardButton(text=weekdays[ind], callback_data=date)]
        sheets[0]['text'] = "Текущая неделя"

    weekdays = get_next_week_string_weekdays()
    for ind, date in enumerate(get_next_week_string_days()):
        # date as callback
        if not user_have_events_on_date(user.id, date):
            continue

        sheets[1]['reply_markup'] = [InlineKeyboardButton(text=weekdays[ind], callback_data=date)]
        sheets[1]['text'] = "Следующая неделя"

    if not sheets[1]['reply_markup']:
        sheets.pop(1)
    if not sheets[0]['reply_markup']:
        sheets.pop(0)

    navigation = [
        InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
        InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW)
    ]

    if len(sheets) == 2:
        sheets[0]['reply_markup'].append(navigation)
        sheets[1]['reply_markup'].append(navigation)

    for ind in range(len(sheets)):
        sheets[ind]['reply_markup'] = InlineKeyboardMarkup(sheets[ind]['reply_markup'])

    return sheets


async def timetable_dates_menu_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data
    telegram_id = update.effective_user.id
    user = fetch_class_user_by_telegram_id(telegram_id)

    if income == LEFT_ARROW:
        sheets = await get_timetable_dates_menu_sheets(update, context)
        context.chat_data['sheet'] -= 1
        context.chat_data['sheet'] += len(sheets)
        context.chat_data['sheet'] %= len(sheets)
        await update_timetable_dates_menu(update, context, query)
        return 0

    if income == RIGHT_ARROW:
        sheets = await get_timetable_dates_menu_sheets(update, context)
        context.chat_data['sheet'] += 1
        context.chat_data['sheet'] %= len(sheets)
        await update_timetable_dates_menu(update, context, query)
        return 0

    context.chat_data['date'] = income
    await update_timetable_date_menu(update, context, query)
    return 1


async def send_timetable_date_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sheet = await get_timetable_date_menu_sheet(update, context)

    context.bot.send_message(chat_id=chat_id, text=sheet['text'], photo=sheet['photo'],
                             reply_markup=sheet['reply_markup'])


async def update_timetable_date_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    sheet = await get_timetable_date_menu_sheet(update, context)

    await update.message.reply_photo(photo=sheet['photo'], reply_markup=sheet['reply_markup'])


async def get_timetable_date_menu_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cur_sheet = int(context.chat_data['sheet'])
    sheets = await get_timetable_date_menu_sheet(update, context)

    return sheets[cur_sheet]


async def get_timetable_date_menu_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = fetch_class_user_by_telegram_id(telegram_id)
    date = context.chat_data['date']
    user_groups = [fetch_group_by_id(user_group['id']) for user_group in fetch_user_groups_by_id(user.id)]

    sheets = []

    for group in user_groups:
        image = fetch_image_by_date_and_group_id(group.id, date)
        if not image:
            continue

        sheets.append(image)

    if not sheets:
        sheets = [[]]

    navigation = [
        InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW)
    ]
    if len(sheets) > 1:
        navigation.insert(0, InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW))
        navigation.append(InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW))

    for ind in range(len(sheets)):
        sheets[ind].append(navigation)
        reply_markup = InlineKeyboardMarkup(sheets[ind])
        sheets[ind] = {'text': f'Расписание на {date}', 'photo': sheets[ind], 'reply_markup': reply_markup}

    return sheets


def user_have_events_on_date(user_id: int, date: str) -> bool:
    user_groups = [fetch_class_group_by_id(user_group['id']) for user_group in fetch_user_groups_by_id(user_id)]

    for group in user_groups:
        image = fetch_image_by_date_and_group_id(date, group.id)
        if image:
            return True

    return False


async def timetable_date_menu_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data
    telegram_id = update.effective_user.id
    user = fetch_class_user_by_telegram_id(telegram_id)

    if income == BACK_ARROW:
        await update_timetable_dates_menu(update, context, query)
        return 0

    if income == LEFT_ARROW:
        sheets = await get_timetable_date_menu_sheets(update, context)
        context.chat_data['sheet'] -= 1
        context.chat_data['sheet'] += len(sheets)
        context.chat_data['sheet'] %= len(sheets)
        await update_timetable_date_menu(update, context, query)
        return 1

    if income == RIGHT_ARROW:
        sheets = await get_timetable_date_menu_sheets(update, context)
        context.chat_data['sheet'] += 1
        context.chat_data['sheet'] %= len(sheets)
        await update_timetable_date_menu(update, context, query)
        return 1


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


ConversationHandler_timetable = ConversationHandler(
    entry_points=[CommandHandler('timetable', start)],

    states={
        0: [CallbackQueryHandler(timetable_dates_menu_response)],
        1: [CallbackQueryHandler(timetable_date_menu_response)]

    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)
