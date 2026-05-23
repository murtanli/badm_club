from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def booking_training_info(
		not_available_stat: bool,
		training_id: str,
		balance: float,
		cost: float,
		user_subscription: list | None
) -> InlineKeyboardMarkup:
	inline_keyboard = []

	if not_available_stat:
		inline_keyboard.append(
			[InlineKeyboardButton(text="❌ Мест нет", callback_data="menu:schedule")]
		)
		return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

	if user_subscription:
		inline_keyboard.append([
			InlineKeyboardButton(text="✅ Записаться по абонементу", callback_data=f"create_booking:subscription-{training_id}")
		])

	if balance < cost:
		inline_keyboard.append([
			InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="menu:balance")
		])
	else:
		inline_keyboard.append([
			InlineKeyboardButton(text="✅ Записаться и списать со счета", callback_data="create_booking:subtract_from_balance")
		])

	inline_keyboard.append(
		[InlineKeyboardButton(text="❓ Правила отмены", callback_data="menu:help")],
	)
	inline_keyboard.append(
		[InlineKeyboardButton(text="◀️ Назад к выбору тип записи", callback_data="menu:schedule")],
	)
	return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
