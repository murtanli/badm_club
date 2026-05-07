from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.api_client import get_subscriptions


async def subscriptions_inline(telegram_id: int) -> InlineKeyboardMarkup:
    keyboard = []

    subscriptions = await get_subscriptions(telegram_id)

    for sub in subscriptions:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{sub['name']} | {sub['price']} руб. ({sub['duration']})",
                callback_data=f"subscription:{sub['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text="◀️ Назад в профиль", callback_data="menu:profile")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)