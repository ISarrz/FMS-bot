from modules.config import get_telegram_message
from modules.database import Group, User
from modules.logger.logger import async_logger

from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
    CallbackContext,
)
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


@async_logger
async def get_ten_grade_sheet()->InlineKeyboardMarkup:
    keyboard = []
    keyboard.append([
        InlineKeyboardButton(text="Β", callback_data="Β"),
        InlineKeyboardButton(text="Γ", callback_data="Γ"),
        InlineKeyboardButton(text="Δ", callback_data="Δ"),
        InlineKeyboardButton(text="Ε", callback_data="Ε"),
        InlineKeyboardButton(text="Ζ", callback_data="Ζ")
    ])
    keyboard.append([
        InlineKeyboardButton(text="Η", callback_data="Η"),
        InlineKeyboardButton(text="Θ", callback_data="Θ"),
        InlineKeyboardButton(text="Ι", callback_data="Ι"),
        InlineKeyboardButton(text="Κ", callback_data="Κ"),
        InlineKeyboardButton(text="Λ", callback_data="Λ"),
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


@async_logger
async def get_eleven_grade_sheet()->InlineKeyboardMarkup:
    keyboard = []
    keyboard.append([
        InlineKeyboardButton(text="Μ", callback_data="Μ"),
        InlineKeyboardButton(text="Ξ", callback_data="Ξ"),
        InlineKeyboardButton(text="Ο", callback_data="Ο"),
        InlineKeyboardButton(text="Π", callback_data="Π"),
        InlineKeyboardButton(text="Ρ", callback_data="Ρ")
    ])
    keyboard.append([
        InlineKeyboardButton(text="Σ", callback_data="Σ"),
        InlineKeyboardButton(text="Τ", callback_data="Τ"),
        InlineKeyboardButton(text="Φ", callback_data="Φ"),
        InlineKeyboardButton(text="Χ", callback_data="Χ"),
        InlineKeyboardButton(text="Ψ", callback_data="Ψ"),
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


@async_logger
async def get_ten_grade_academic_groups_sheet() ->InlineKeyboardMarkup:
    keyboard = []
    keyboard.append([
        InlineKeyboardButton(text="1", callback_data="1 группа"),
        InlineKeyboardButton(text="2", callback_data="2 группа"),
        InlineKeyboardButton(text="3", callback_data="3 группа"),
        InlineKeyboardButton(text="4", callback_data="4 группа"),
        InlineKeyboardButton(text="5", callback_data="5 группа"),
        InlineKeyboardButton(text="6", callback_data="6 группа"),
    ])
    keyboard.append([
        InlineKeyboardButton(text="7", callback_data="7 группа"),
        InlineKeyboardButton(text="8", callback_data="8 группа"),
        InlineKeyboardButton(text="9", callback_data="9 группа"),
        InlineKeyboardButton(text="10", callback_data="10 группа"),
        InlineKeyboardButton(text="11", callback_data="11 группа"),
        InlineKeyboardButton(text="12", callback_data="12 группа"),
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


@async_logger
async def get_eleven_grade_academic_groups_sheet() -> InlineKeyboardMarkup:
    keyboard = []
    keyboard.append([
        InlineKeyboardButton(text="1", callback_data="1 группа"),
        InlineKeyboardButton(text="2", callback_data="2 группа"),
        InlineKeyboardButton(text="3", callback_data="3 группа"),
        InlineKeyboardButton(text="4", callback_data="4 группа"),
        InlineKeyboardButton(text="5", callback_data="5 группа"),
    ])
    keyboard.append([
        InlineKeyboardButton(text="6", callback_data="6 группа"),
        InlineKeyboardButton(text="7", callback_data="7 группа"),
        InlineKeyboardButton(text="8", callback_data="8 группа"),
        InlineKeyboardButton(text="9", callback_data="9 группа"),
        InlineKeyboardButton(text="10", callback_data="10 группа")
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup
