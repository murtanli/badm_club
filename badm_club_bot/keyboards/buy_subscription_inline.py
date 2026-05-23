from decimal import Decimal

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.api_client import get_training_subs
import logging
logger = logging.getLogger("bot_buy_subs")


async def subscriptions_inline(telegram_id: int) -> InlineKeyboardMarkup:
    keyboard = []

    subscriptions = await get_training_subs(telegram_id)
    for sub in subscriptions['available_subscriptions']:
        price = Decimal(str(sub['price']))
        keyboard.append([
            InlineKeyboardButton(
                text=f"🎫 {sub['name']} ({price:.1f} ₽)",
                callback_data=f"buy_subscription:id-{sub['id']}"
            )
        ])

    keyboard.append([InlineKeyboardButton(text="◀️ Назад в профиль", callback_data="menu:profile")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)