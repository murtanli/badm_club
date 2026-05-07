from decimal import Decimal
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def training_subs_inline(training_subs: list[dict]) -> InlineKeyboardMarkup:
	keyboard = []
	for sub in training_subs:
		price = Decimal(str(sub['price']))
		keyboard.append([
			InlineKeyboardButton(
				text=f"🎫 {sub['name']} ({price:.1f} ₽)",
				callback_data=f"buy_subscription:{sub['id']}"
			)
		])
	keyboard.append([InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="profile:top_up_balance")])
	keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="menu:back")])
	return InlineKeyboardMarkup(inline_keyboard=keyboard)
