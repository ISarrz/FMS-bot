from modules.time import get_current_week_string_days, get_current_week_string_weekdays
from modules.database.group.group import Group
from modules.telegram_int.constants import *
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
    CallbackContext,
    filters
)
from modules.database import User
from modules.logger.logger import async_logger


def get_settings_menu_sheet(user: User):
    keyboard = []

    text = f"Уведомления {TICK if user.settings.notifications else CROSS}"
    keyboard.append([InlineKeyboardButton(text=text, callback_data="notifications")])
    text = "Режим: изображение" if user.settings.mode == "image" else "Режим: текст"
    keyboard.append([InlineKeyboardButton(text=text, callback_data="mode")])
    keyboard.append([InlineKeyboardButton(text="Группы", callback_data="groups")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup




def get_groups_menu_sheets(update: Update, context: CallbackContext):
    main_group = context.chat_data['settings_group']
    sheets = []
    MAX_LENGTH = 5
    user = User(telegram_id=update.effective_chat.id)
    for group in main_group.children:
        text = group.name
        if group.id in [ug.id for ug in user.groups]:
            text = f"{TICK} " + text

        if not sheets or len(sheets[-1]) >= MAX_LENGTH:
            sheets.append([])

        sheets[-1].append([InlineKeyboardButton(text=text, callback_data=group.id)])

    for i in range(len(sheets)):
        sheet = sheets[i]
        if len(sheets) > 1:
            sheet.append([InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
                          InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
                          InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW)
                          ])
        else:
            sheet.append([InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW)])
        sheets[i] = InlineKeyboardMarkup(sheet)


    return sheets
