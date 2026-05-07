from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def choose_schedule_inline():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton(text="🏋️ Записи по тренерам", callback_data="schedule:sports_trainers")],
			[InlineKeyboardButton(text="🏟️ Записи по залам", callback_data="schedule:sports_gyms")],
			[InlineKeyboardButton(text="◀️ Назад", callback_data="menu:back")],
		]
	)
