from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def back_inline():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="menu:back")],
        ]
    )