from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def back_inline(callback_data: str = "menu:back") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data=callback_data)]
        ]
    )
