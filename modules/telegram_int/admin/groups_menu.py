from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
)
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from modules.database_api import *
from modules.logger import *
from modules.telegram_int.admin.symbols import *
from modules.logger.logger import async_logger, logger
@async_logger
async def update_groups_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    group_id = context.chat_data['group']
    group = fetch_class_group_by_id(group_id)
    child = fetch_all_class_child_by_id(group_id)
    sheet = await get_groups_menu_sheet(update, context)

    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])

@async_logger
async def send_groups_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = context.chat_data['group']
    group = fetch_class_group_by_id(group_id)
    child = fetch_all_class_child_by_id(group_id)
    sheet = await get_groups_menu_sheet(update, context)
    context.chat_data['sheet'] = 0

    await update.message.reply_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def get_groups_menu_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sheet_ind = context.chat_data['sheet']
    sheets = await get_groups_menu_sheets(update, context)

    return sheets[sheet_ind]


async def get_groups_menu_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        InlineKeyboardButton(text=ADD, callback_data=ADD),
        InlineKeyboardButton(text=EDIT, callback_data=EDIT)
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

@async_logger
async def update_add_group_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    sheet = await get_add_group_menu_sheet(update, context)

    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def get_add_group_menu_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parent_id = int(context.chat_data['group'])

    text = ("Введите данные группы:\n"
            "name:\n"
            "Или отмените действие: cancel")
    return {"text": text, "reply_markup": None}

@async_logger
async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    income = update.message.text
    if income != "cancel":
        parent_id = int(context.chat_data['group'])
        group_name = income
        group_id = insert_group(name=group_name, about=str(None))
        insert_groups_relation(parent_id=parent_id, child_id=group_id)
        context.chat_data['group'] = group_id

    await send_groups_menu(update, context)
    return 2

@async_logger
async def send_edit_group_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = context.chat_data['group']
    group = fetch_class_group_by_id(group_id)
    child = fetch_all_class_child_by_id(group_id)
    sheet = await get_edit_group_menu_sheet(update, context)
    context.chat_data['sheet'] = 0

    await update.message.reply_text(text=sheet["text"], reply_markup=sheet["reply_markup"])

@async_logger
async def update_edit_group_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    sheet = await get_edit_group_menu_sheet(update, context)

    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def get_edit_group_menu_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = context.chat_data['group']
    group = fetch_class_group_by_id(group_id)
    keyboard = []

    keyboard.append([InlineKeyboardButton(text=f"name: {group.name}", callback_data="name")])
    keyboard.append([
        InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
        InlineKeyboardButton(text=DELETE, callback_data=DELETE),
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)

    return {"text": f"Редактирование группы: {group.name}", "reply_markup": reply_markup}

@async_logger
async def edit_group_menu_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await update_groups_menu(update, context, query)
        return 2

    if income == DELETE:
        await update_delete_group_menu(update, context, query)
        return 6

    context.chat_data['edit_group_field'] = income
    await update_edit_group_field_menu(update, context, query)
    return 5

@async_logger
async def update_edit_group_field_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    text = ("Введите данные\n"
            "Или отмените действие: cancel")
    sheet = {"text": text, "reply_markup": None}

    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])

@async_logger
async def edit_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    income = update.message.text
    group_id = int(context.chat_data['group'])
    group = fetch_class_group_by_id(group_id)

    if income != "cancel" and context.chat_data['edit_group_field'] == "name":
        update_group_by_id(group.id, name=income, about=group.about)

    await send_edit_group_menu(update, context)
    return 4

@async_logger
async def update_delete_group_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    group_id = int(context.chat_data['group'])
    group = fetch_class_group_by_id(group_id)

    keyboard = []
    keyboard.append([
        InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
        InlineKeyboardButton(text=CANCEL, callback_data=CANCEL),
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)

    sheet = {"text": f"Удалить: {group.name}?", "reply_markup": reply_markup}

    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])

@async_logger
async def delete_group_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data
    group_id = int(context.chat_data['group'])

    if income == SUBMIT and group_id != 1:
        parent = fetch_class_parent_by_id(group_id)
        context.chat_data['group'] = parent.id
        delete_group_and_relations_by_id(group_id)
        await update_groups_menu(update, context, query)
        return 2

    if income == CANCEL or group_id == 1:
        await update_edit_group_menu(update, context, query)
        return 4



