from modules.telegram.admin.events_menu import *
from modules.telegram.admin.groups_menu import *
from modules.logger import *

ADMIN_CHAT_ID = get_config_field("admin_chat_id")


@async_logger
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    if not fetch_user_by_telegram_id(telegram_id):
        user_id = insert_user(telegram_id)
        insert_user_notifications_by_id(user_id)

    await send_settings_menu(update, context)
    return 0


@async_logger
async def send_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sheet = await get_settings_menu_sheet(update, context)
    context.chat_data['group'] = 1
    context.chat_data['sheet'] = 0

    await update.message.reply_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


@async_logger
async def update_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    sheet = await get_settings_menu_sheet(update, context)
    context.chat_data['group'] = 1
    context.chat_data['sheet'] = 0

    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def get_settings_menu_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = fetch_class_user_by_telegram_id(telegram_id)
    notifications_state = int(fetch_user_notifications(user.id)['value'])
    notif_text = f'Уведомления  {"🗸" if notifications_state else "⨯"}'
    keyboard = [[InlineKeyboardButton(text="Группы", callback_data="groups")],
                [InlineKeyboardButton(text=notif_text, callback_data="notifications")]
                ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    sheet = {"text": "Настройки", "reply_markup": reply_markup}

    return sheet


@async_logger
async def settings_menu_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data
    telegram_id = update.effective_user.id
    user = fetch_class_user_by_telegram_id(telegram_id)
    notifications_state = 1 - int(fetch_user_notifications(user.id)['value'])
    if income == "groups":
        await update_settings_groups_mode_menu(update, context, query)
        return 1

    if income == "notifications":
        update_notifications_by_id(user.id, notifications_state)
        await update_settings_menu(update, context, query)
        return 0


@async_logger
async def update_settings_groups_mode_menu(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                           query: CallbackQueryHandler):
    sheet = await get_settings_groups_menu_sheet(update, context)

    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def get_settings_groups_menu_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cur_sheet = int(context.chat_data['sheet'])
    sheets = await get_setting_groups_menu_sheets(update, context)

    return sheets[cur_sheet]


async def get_setting_groups_menu_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = fetch_class_user_by_telegram_id(telegram_id)
    group_id = int(context.chat_data['group'])
    group = fetch_class_group_by_id(group_id)

    user_groups = fetch_user_groups_by_parent_group_id(user.id, group.id)
    user_groups = [DbGroup(id=user_group['id'], name=user_group['name'], about=user_group['about']) for user_group in
                   user_groups]

    MAX_SHEET_LEN = 5
    sheets = [[]]

    for user_group in user_groups:
        if len(sheets[-1]) > MAX_SHEET_LEN:
            sheets.append([])

        sheets[-1].append([InlineKeyboardButton(text=user_group.name, callback_data=user_group.id)])

    navigation = [
        InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
        InlineKeyboardButton(text=ADD, callback_data=ADD),
    ]

    if group.id != 1:
        navigation.append(InlineKeyboardButton(text=DELETE, callback_data=DELETE))

    if len(sheets) > 1:
        navigation.insert(0, InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW))
        navigation.append(InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW))

    for i in range(len(sheets)):
        sheets[i].append(navigation)
        reply_markup = InlineKeyboardMarkup(sheets[i])
        text = f"Настройки, группа {group.name}"
        if len(sheets) > 1:
            text += f'; №{int(context.chat_data["sheet"]) + 1}'

        sheets[i] = {"text": text, "reply_markup": reply_markup}

    return sheets


@async_logger
async def settings_groups_mode_menu_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data
    telegram_id = update.effective_user.id
    user = fetch_class_user_by_telegram_id(telegram_id)
    group_id = int(context.chat_data['group'])
    group = fetch_class_group_by_id(group_id)

    if income == BACK_ARROW:
        context.chat_data['sheet'] = 0
        group_id = int(context.chat_data['group'])
        if group_id == 1:
            context.chat_data['sheet'] = 0
            await update_settings_menu(update, context, query)
            return 0

        group = fetch_class_group_by_id(group_id)
        parent = fetch_parent_by_id(group.id)
        parent = fetch_class_group_by_id(parent['id'])

        context.chat_data['group'] = parent.id

        await update_settings_groups_mode_menu(update, context, query)

        return 1

    if income == LEFT_ARROW:
        sheets = await get_setting_groups_menu_sheets(update, context)
        context.chat_data['sheet'] -= 1
        context.chat_data['sheet'] += len(sheets)
        context.chat_data['sheet'] %= len(sheets)

        await update_settings_groups_mode_menu(update, context, query)
        return 1

    if income == RIGHT_ARROW:
        sheets = await get_setting_groups_menu_sheets(update, context)
        context.chat_data['sheet'] += 1
        context.chat_data['sheet'] %= len(sheets)

        await update_settings_groups_mode_menu(update, context, query)
        return 1

    if income == DELETE:
        await update_settings_delete_group_menu(update, context, query)
        return 2

    if income == ADD:
        context.chat_data['sheet'] = 0
        await update_settings_add_group_menu(update, context, query)
        return 3

    context.chat_data['group'] = int(income)
    context.chat_data['sheet'] = 0
    await update_settings_groups_mode_menu(update, context, query)
    return 1


@async_logger
async def update_settings_delete_group_menu(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                            query: CallbackQueryHandler):
    keyboard = [[InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
                 InlineKeyboardButton(text=CANCEL, callback_data=CANCEL)]
                ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    sheet = {"text": "Удалить группу?", "reply_markup": reply_markup}

    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


@async_logger
async def settings_delete_group_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data
    telegram_id = update.effective_user.id
    user = fetch_class_user_by_telegram_id(telegram_id)
    group_id = int(context.chat_data['group'])
    group = fetch_class_group_by_id(group_id)

    if income == SUBMIT:
        context.chat_data['sheet'] = 0
        if group_id == 1:
            context.chat_data['sheet'] = 0
            await update_settings_menu(update, context, query)
            return 0

        parent = fetch_parent_by_id(group.id)
        parent = fetch_class_group_by_id(parent['id'])

        context.chat_data['group'] = parent.id

        context.chat_data['sheet'] = 0
        delete_user_group_and_relations(user.id, group.id)
        await update_settings_groups_mode_menu(update, context, query)
        return 1

    if income == CANCEL:
        context.chat_data['sheet'] = 0
        await update_settings_groups_mode_menu(update, context, query)
        return 1


@async_logger
async def update_settings_add_group_menu(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                         query: CallbackQueryHandler):
    sheet = await get_setting_add_menu_sheet(update, context)

    await query.edit_message_text(text=sheet["text"], reply_markup=sheet["reply_markup"])


async def get_setting_add_menu_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cur_sheet = int(context.chat_data['sheet'])
    sheets = await get_setting_add_menu_sheets(update, context)

    return sheets[cur_sheet]


async def get_setting_add_menu_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = fetch_class_user_by_telegram_id(telegram_id)
    group_id = int(context.chat_data['group'])
    group = fetch_class_group_by_id(group_id)

    child = fetch_all_class_child_by_id(group_id)

    MAX_SHEET_LEN = 5
    sheets = [[]]

    for user_group in child:
        if len(sheets[-1]) > MAX_SHEET_LEN:
            sheets.append([])

        sheets[-1].append([InlineKeyboardButton(text=user_group.name, callback_data=user_group.id)])

    navigation = [
        InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW)
    ]

    if len(sheets) > 1:
        navigation.insert(0, InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW))
        navigation.append(InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW))

    for i in range(len(sheets)):
        sheets[i].append(navigation)
        reply_markup = InlineKeyboardMarkup(sheets[i])
        text = f"Добавление группы"
        if len(sheets) > 1:
            text += f'; №{int(context.chat_data["sheet"]) + 1}'

        sheets[i] = {"text": text, "reply_markup": reply_markup}

    return sheets


@async_logger
async def settings_add_group_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data
    telegram_id = update.effective_user.id
    user = fetch_class_user_by_telegram_id(telegram_id)
    group_id = int(context.chat_data['group'])
    group = fetch_class_group_by_id(group_id)

    if income == BACK_ARROW:
        context.chat_data['sheet'] = 0
        await update_settings_groups_mode_menu(update, context, query)
        return 1

    if income == LEFT_ARROW:
        sheets = await get_setting_add_menu_sheets(update, context)
        context.chat_data['sheet'] -= 1
        context.chat_data['sheet'] += len(sheets)
        context.chat_data['sheet'] %= len(sheets)
        await update_settings_add_group_menu(update, context)
        return 3

    if income == RIGHT_ARROW:
        sheets = await get_setting_add_menu_sheets(update, context)
        context.chat_data['sheet'] += 1
        context.chat_data['sheet'] %= len(sheets)
        await update_settings_add_group_menu(update, context, query)
        return 3

    seq = fetch_groups_sequence(int(income))
    seq = [fetch_class_group_by_id(seq_group['id']) for seq_group in seq]

    user_groups = fetch_user_groups_by_id(user.id)
    user_groups = [fetch_class_group_by_id(user_group['id']) for user_group in user_groups]
    for cur_group in seq:
        if cur_group not in user_groups:
            insert_user_group(user.id, cur_group.id)

    context.chat_data['sheet'] = 0
    await update_settings_groups_mode_menu(update, context, query)
    return 1


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


ConversationHandler_settings = ConversationHandler(
    entry_points=[CommandHandler('settings', start)],

    states={
        0: [CallbackQueryHandler(settings_menu_response)],
        1: [CallbackQueryHandler(settings_groups_mode_menu_response)],
        2: [CallbackQueryHandler(settings_delete_group_response)],
        3: [CallbackQueryHandler(settings_add_group_response)],

    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)
