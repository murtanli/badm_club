from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def profile_inline():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎫 Купить абонемент", callback_data="profile:buy_subscription")],
            [InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="profile:top_up_balance")],
            [InlineKeyboardButton(text="🧾 История транзакций", callback_data="profile:transaction_history")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="profile:back")],
        ]
    )