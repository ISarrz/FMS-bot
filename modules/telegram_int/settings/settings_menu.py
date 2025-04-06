from modules.telegram_int.admin.events_menu import *
from modules.telegram_int.admin.groups_menu import *
from modules.logger import *
from modules.logger.logger import async_logger, logger

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
    notif_text = f'Уведомления  {"✓︎" if notifications_state else "⨯"}'
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
        await update_settings_grade_choice(update, context, query)
        return 1

    if income == "notifications":
        update_notifications_by_id(user.id, notifications_state)
        await update_settings_menu(update, context, query)
        return 0


async def update_settings_grade_choice(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    keyboard = [
        [InlineKeyboardButton(text="10 класс", callback_data="10 класс"),
         InlineKeyboardButton(text="11 класс", callback_data="11 класс"),
         ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Выберите параллель", reply_markup=reply_markup)


async def settings_grade_choice_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data
    context.chat_data['grade'] = income

    await update_settings_class_choice(update, context, query)
    return 2


async def update_settings_class_choice(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                       query: CallbackQueryHandler):
    if context.chat_data['grade'] == '10 класс':
        keyboard = [
            [InlineKeyboardButton(text="Μ", callback_data="Μ"),
             InlineKeyboardButton(text="Ξ", callback_data="Ξ"),
             InlineKeyboardButton(text="Ο", callback_data="Ο"),
             InlineKeyboardButton(text="Π", callback_data="Π"),
             InlineKeyboardButton(text="Ρ", callback_data="Ρ")
             ],
            [
                InlineKeyboardButton(text="Σ", callback_data="Σ"),
                InlineKeyboardButton(text="Τ", callback_data="Τ"),
                InlineKeyboardButton(text="Φ", callback_data="Φ"),
                InlineKeyboardButton(text="Χ", callback_data="Χ"),
                InlineKeyboardButton(text="Ψ", callback_data="Ψ")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    elif context.chat_data['grade'] == '11 класс':
        keyboard = [
            [InlineKeyboardButton(text="Β", callback_data="Β"),
             InlineKeyboardButton(text="Γ", callback_data="Γ"),
             InlineKeyboardButton(text="Δ", callback_data="Δ"),
             InlineKeyboardButton(text="Ε", callback_data="Ε"),
             InlineKeyboardButton(text="Ζ", callback_data="Ζ")
             ],
            [
                InlineKeyboardButton(text="Η", callback_data="Η"),
                InlineKeyboardButton(text="Θ", callback_data="Θ"),
                InlineKeyboardButton(text="Ι", callback_data="Ι"),
                InlineKeyboardButton(text="Κ", callback_data="Κ"),
                InlineKeyboardButton(text="Λ", callback_data="Λ")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text="Выберите класс", reply_markup=reply_markup)


async def settings_class_choice_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data
    context.chat_data['class'] = income

    await update_settings_group_choice(update, context, query)
    return 3


async def update_settings_group_choice(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                       query: CallbackQueryHandler):
    keyboard = [
        [InlineKeyboardButton(text="Группа А", callback_data="Группа А"),
         InlineKeyboardButton(text="Группа Б", callback_data="Группа Б"),
         ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text="Выберите группу класса", reply_markup=reply_markup)


async def settings_group_choice_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data
    context.chat_data['group'] = income
    await update_settings_academ_group_choice(update, context, query)
    return 4


async def update_settings_academ_group_choice(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                              query: CallbackQueryHandler):
    keyboard = [
        [InlineKeyboardButton(text="1", callback_data="1 группа"),
         InlineKeyboardButton(text="2", callback_data="2 группа"),
         InlineKeyboardButton(text="3", callback_data="3 группа"),
         InlineKeyboardButton(text="4", callback_data="4 группа"),
         InlineKeyboardButton(text="5", callback_data="5 группа")], [
            InlineKeyboardButton(text="6", callback_data="6 группа"),
            InlineKeyboardButton(text="7", callback_data="7 группа"),
            InlineKeyboardButton(text="8", callback_data="8 группа"),
            InlineKeyboardButton(text="9", callback_data="9 группа"),
            InlineKeyboardButton(text="10", callback_data="10 группа")], [
            InlineKeyboardButton(text="11", callback_data="11 группа"),
            InlineKeyboardButton(text="12", callback_data="12 группа"),
            InlineKeyboardButton(text="13", callback_data="13 группа"),
            InlineKeyboardButton(text="14", callback_data="14 группа"),
            InlineKeyboardButton(text="15", callback_data="15 группа")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text="Выберите группу академ дня", reply_markup=reply_markup)


async def settings_academ_group_choice_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data
    context.chat_data['academ_group'] = income

    await add_groups(update, context, query)

    await update_settings_succeed(update, context, query)

    return ConversationHandler.END


async def add_groups(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    user = fetch_class_user_by_telegram_id(update.effective_user.id)
    delete_user_groups(user.id)
    delete_user_updates(user.id)

    grade = context.chat_data['grade']
    cls = context.chat_data['class']
    group = context.chat_data['group']

    academ_group = context.chat_data['academ_group']
    fms_group_id = 1
    grade_id = fetch_group_by_parent_id_and_name(fms_group_id, grade).id
    class_id = fetch_group_by_parent_id_and_name(grade_id, cls).id
    group_id = fetch_group_by_parent_id_and_name(class_id, group).id

    academ_id = fetch_group_by_parent_id_and_name(grade_id, "Академическая группа").id
    academ_group_id = fetch_group_by_parent_id_and_name(academ_id, academ_group).id

    insert_user_group(user.id, fms_group_id)
    insert_user_group(user.id, grade_id)
    insert_user_group(user.id, class_id)
    insert_user_group(user.id, group_id)
    insert_user_group(user.id, academ_id)
    insert_user_group(user.id, academ_group_id)


async def update_settings_succeed(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQueryHandler):
    await query.edit_message_text(text="Группы успешно добавлены")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


ConversationHandler_settings = ConversationHandler(
    entry_points=[CommandHandler('settings', start)],

    states={
        0: [CallbackQueryHandler(settings_menu_response)],
        1: [CallbackQueryHandler(settings_grade_choice_response)],
        2: [CallbackQueryHandler(settings_class_choice_response)],
        3: [CallbackQueryHandler(settings_group_choice_response)],
        4: [CallbackQueryHandler(settings_academ_group_choice_response)]
    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)
