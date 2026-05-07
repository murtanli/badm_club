from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Запись")],
            [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="💰 Баланс")],
            [KeyboardButton(text="❓ Помощь"), KeyboardButton(text="ℹ️ О боте")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )


def main_menu_inline():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Запись", callback_data="menu:schedule")],
            [InlineKeyboardButton(text="👤 Профиль", callback_data="menu:profile")],
            [InlineKeyboardButton(text="💰 Баланс", callback_data="menu:balance")],
            [InlineKeyboardButton(text="❓ Помощь", callback_data="menu:help")],
            [InlineKeyboardButton(text="ℹ️ О боте", callback_data="menu:about")]
        ]
    )