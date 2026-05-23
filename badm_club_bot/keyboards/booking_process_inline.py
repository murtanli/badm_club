from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def booking_process_inline(
		enough_money: bool,
		price: float,
		subscription_id: int
) -> InlineKeyboardMarkup:
	inline_keyboard = []

	if enough_money:
		inline_keyboard.append([
			InlineKeyboardButton(
				text="🏛️ Оплатить с баланса",
				callback_data=f"balance:pay_from_balance-{subscription_id}"
			)
		])

	inline_keyboard.append([
		InlineKeyboardButton(
			text="💳 Оплатить картой",
			callback_data=f"balance:pay_by_card:{price:.1f}"
		)
	])

	inline_keyboard.append([
		InlineKeyboardButton(text="◀️ Назад", callback_data="menu:back")
	])

	return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
