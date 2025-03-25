from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from modules.files_api import get_config_field
from modules.database_api import *
from modules.time import *
from modules.telegram.admin.symbols import *


async def update_dates_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    sheet = await get_dates_menu_sheet(update, context)
    context.chat_data['group'] = 1
    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def get_dates_menu_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sheets = await get_dates_menu_sheets(update, context)
    cur_sheet = sheets[context.chat_data['sheet']]

    return cur_sheet


async def get_dates_menu_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sheets = []
    keyboard = []
    for weekday_string in get_current_week_string_weekdays():
        # date as callback
        keyboard.append([InlineKeyboardButton(text=weekday_string, callback_data=weekday_string.split()[1])])

    keyboard.append([
        InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
        InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
        InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW)
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    sheets.append({"text": "Текущая неделя", "reply_markup": reply_markup})

    keyboard = []
    for weekday_string in get_next_week_string_weekdays():
        # date as callback
        keyboard.append([InlineKeyboardButton(text=weekday_string, callback_data=weekday_string.split()[1])])

    keyboard.append([
        InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
        InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
        InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW)
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    sheets.append({"text": "Следующая неделя", "reply_markup": reply_markup})

    return sheets


async def update_events_groups_mode_menu(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                         query: CallbackQueryHandler):
    group_id = context.chat_data['group']
    group = fetch_class_group_by_id(group_id)
    child = fetch_all_class_child_by_id(group_id)
    sheet = await get_events_groups_mode_menu_sheet(update, context)

    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def send_events_groups_mode_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = context.chat_data['group']
    group = fetch_class_group_by_id(group_id)
    child = fetch_all_class_child_by_id(group_id)
    sheet = await get_events_groups_mode_menu_sheet(update, context)
    context.chat_data['sheet'] = 0

    await update.message.reply_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def get_events_groups_mode_menu_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sheet_ind = context.chat_data['sheet']
    sheets = await get_events_groups_mode_menu_sheets(update, context)

    return sheets[sheet_ind]


async def get_events_groups_mode_menu_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = int(context.chat_data['group'])
    group = fetch_class_group_by_id(group_id)
    child = fetch_all_class_child_by_id(group_id)
    MAX_SHEET_SIZE = 5
    sheets = [[]]
    for child_group in child:
        if len(sheets[-1]) > MAX_SHEET_SIZE:
            sheets.append([])
        sheets[-1].append([InlineKeyboardButton(text=child_group.name, callback_data=child_group.id)])

    navigation = [
        InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
        InlineKeyboardButton(text="events", callback_data="events")
    ]
    if len(sheets) > 1:
        navigation.insert(0, InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW))
        navigation.append(InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW))

    for ind in range(len(sheets)):
        sheets[ind].append(navigation)
        reply_markup = InlineKeyboardMarkup(sheets[ind])
        text = f"Группа {group.name}"
        if len(sheets) > 1:
            text += f"; №{ind + 1}"

        sheets[ind] = {
            "text": text,
            "reply_markup": reply_markup,
        }

    return sheets


async def update_events_events_mode_menu(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                         query: CallbackQueryHandler):
    group_id = context.chat_data['group']
    group = fetch_class_group_by_id(group_id)
    child = fetch_all_class_child_by_id(group_id)
    sheet = await get_events_events_mode_menu_sheet(update, context)

    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def send_events_events_mode_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = context.chat_data['group']
    group = fetch_class_group_by_id(group_id)
    child = fetch_all_class_child_by_id(group_id)
    sheet = await get_events_events_mode_menu_sheet(update, context)
    context.chat_data['sheet'] = 0

    await update.message.reply_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def get_events_events_mode_menu_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sheet_ind = context.chat_data['sheet']
    sheets = await get_events_events_mode_menu_sheets(update, context)

    return sheets[sheet_ind]


async def get_events_events_mode_menu_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = int(context.chat_data['group'])
    group = fetch_class_group_by_id(group_id)
    date = context.chat_data['date']
    events = fetch_group_events_by_group_id_and_date(group_id, date)
    events = [
        DbEvent(id=event['id'], name=event['name'],
                about=event['about'], start=event['start'], end=event['end'],
                place=event['place'], owner=event['owner'], date=event['date'])
        for event in events]

    MAX_SHEET_SIZE = 5
    sheets = [[]]
    for event in events:
        if len(sheets[-1]) > MAX_SHEET_SIZE:
            sheets.append([])
        text = f"{event.name}: {event.start}-{event.end}; {event.place}; {event.owner}"
        sheets[-1].append([InlineKeyboardButton(text=text, callback_data=event.id)])

    navigation = [
        InlineKeyboardButton(text=ADD, callback_data=ADD),
        InlineKeyboardButton(text="groups", callback_data="groups")
    ]
    if len(sheets) > 1:
        navigation.insert(0, InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW))
        navigation.append(InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW))

    for ind in range(len(sheets)):
        sheets[ind].append(navigation)
        reply_markup = InlineKeyboardMarkup(sheets[ind])
        text = f"Группа {group.name}; дата {date}"
        if len(sheets) > 1:
            text += f"; №{ind + 1}"

        sheets[ind] = {
            "text": text,
            "reply_markup": reply_markup,
        }

    return sheets


async def update_add_event_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    sheet = await get_add_event_menu_sheet(update, context)

    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def get_add_event_menu_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parent_id = int(context.chat_data['group'])
    date = context.chat_data['date']

    text = ("Введите данные события:\n"
            "name:\n"
            "start:\n"
            "end:\n"
            "owner:\n"
            "place:\n"
            "Или отмените действие: cancel")
    return {"text": text, "reply_markup": None}


async def add_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    income = update.message.text
    if income != "cancel":
        parent_id = int(context.chat_data['group'])
        income = income.split('\n')
        event_name = income[0]
        event_start = income[1]
        event_end = income[2]
        event_owner = income[3]
        event_place = income[4]
        date = context.chat_data['date']

        event_id = insert_event(name=event_name, start=event_start,
                                end=event_end, owner=event_owner,
                                place=event_place,
                                about=str(None), date=date)
        insert_group_event(parent_id, event_id)
        context.chat_data['event'] = event_id
        await send_edit_event_menu(update, context)
        return 9

    await send_events_events_mode_menu(update, context)
    return 7


async def send_edit_event_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sheet = await get_edit_event_menu_sheet(update, context)
    context.chat_data['sheet'] = 0

    await update.message.reply_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def update_edit_event_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    sheet = await get_edit_event_menu_sheet(update, context)

    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def get_edit_event_menu_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_id = int(context.chat_data['event'])
    event = fetch_class_event_by_id(event_id)
    keyboard = []

    keyboard.append([InlineKeyboardButton(text=f"name: {event.name}", callback_data="name")])
    keyboard.append([ InlineKeyboardButton(text=f"start: {event.start}", callback_data="start")])
    keyboard.append([ InlineKeyboardButton(text=f"end: {event.end}", callback_data="end")])
    keyboard.append([InlineKeyboardButton(text=f"owner: {event.owner}", callback_data="owner")])
    keyboard.append([InlineKeyboardButton(text=f"place: {event.place}", callback_data="place")])
    keyboard.append([InlineKeyboardButton(text=f"date: {event.date}", callback_data="date")])

    keyboard.append([
        InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
        InlineKeyboardButton(text=DELETE, callback_data=DELETE),
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)

    return {"text": f"Редактирование события: {event.name}", "reply_markup": reply_markup}


async def edit_event_menu_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        context.chat_data['sheet'] = 0
        await update_events_events_mode_menu(update, context, query)
        return 7

    if income == DELETE:
        await update_delete_event_menu(update, context, query)
        return 11

    context.chat_data['edit_group_field'] = income
    await update_edit_event_field_menu(update, context, query)
    return 10


async def update_edit_event_field_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    text = ("Введите данные\n"
            "Или отмените действие: cancel")
    sheet = {"text": text, "reply_markup": None}

    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def edit_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    income = update.message.text
    event_id = int(context.chat_data['event'])
    event = fetch_class_event_by_id(event_id)

    if income == "cancel":
        await send_edit_event_menu(update, context)
        return 9

    if context.chat_data['edit_group_field'] == "name":
        event.name = income

    if context.chat_data['edit_group_field'] == "start":
        event.start = income

    if context.chat_data['edit_group_field'] == "end":
        event.end = income

    if context.chat_data['edit_group_field'] == "owner":
        event.owner = income

    if context.chat_data['edit_group_field'] == "place":
        event.place = income

    if context.chat_data['edit_group_field'] == "date":
        event.date = income

    update_event_by_id(event_id=event.id, name=event.name,
                       about=event.about, date=event.date, start=event.start,
                       end=event.end, owner=event.owner, place=event.place)
    await send_edit_event_menu(update, context)
    return 9


async def update_delete_event_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    event_id = int(context.chat_data['event'])
    event = fetch_class_event_by_id(event_id)

    keyboard = []
    keyboard.append([
        InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
        InlineKeyboardButton(text=CANCEL, callback_data=CANCEL),
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)

    sheet = {"text": f"Удалить: {event.name}?", "reply_markup": reply_markup}

    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def delete_event_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data
    event_id = int(context.chat_data['event'])
    parent_id = int(context.chat_data['group'])

    if income == SUBMIT:
        delete_group_event_by_event_id(event_id)
        delete_event_by_id(event_id)

        context.chat_data['sheet'] = 0
        await update_events_events_mode_menu(update, context, query)
        return 7

    if income == CANCEL:
        context.chat_data['sheet'] = 0
        await update_edit_event_menu(update, context, query)
        return 9


