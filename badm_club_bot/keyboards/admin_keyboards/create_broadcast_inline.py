from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_broadcast_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Отправить объявление", callback_data="admin_broadcast:send")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin:menu")],
    ])