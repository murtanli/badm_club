
def session_text_busy(
		type_name: str,
		start_datetime: str,
		end_datetime: str,
		gym_name: str,
		gym_address: str,
		bookings_count: int,
		max_participants: int,
		participants: list,
) -> str:
	start_date, start_time = start_datetime.split(" ")
	end_date, end_time = end_datetime.split(" ")
	lines = (
		"🔥 Тренировка ЗАПОЛНЕНА!\n"
		f"Зал: {gym_name} ({gym_address})\n"
		f"Дата: {start_date}\n"
		f"Время: {start_time}-{end_time}\n"
		f"Тип: {type_name}\n"
		f"Участников: {bookings_count}/{max_participants} 🔥\n"
		"Список участников: ")

	for i, p in enumerate(participants, 1):
		full_name = f" {p['full_name']}" if p.get('full_name') else ''
		lines += f"{i}. {full_name}\n"

	lines += "\n"
	lines += ("Совет: Попробуйте выбрать другую тренировку или проверяйте наличие отмен!")

	return lines

def session_text(
		type_name: str,
		type_description: str,
		weekday: str,
		start_datetime: str,
		end_datetime: str,
		gym_name: str,
		gym_address: str,
		trainer_name: str,
		cost: float,
		user_balance: int,
		bookings_count: int,
		max_participants: int,
		participants: list,
) -> str:
	if cost > user_balance:
		difference = cost - user_balance
		balance_line = (
			f"💳 Стоимость: {cost} ₽ (баланс {user_balance} ₽)\n"
			f"⚠️ Для записи, пополните баланс на {int(difference)} ₽\n"
		)
	else:
		balance_line = f"💳 Стоимость: {cost} ₽ (баланс {user_balance} ₽)\n"

	end_time = end_datetime.split(" ")[1]

	caption = (
		f"*{type_name}*\n"
		f"{type_description}\n\n"
		f"🗓 {weekday}, {start_datetime}-{end_time}\n"
		f"📍 {gym_name} ({gym_address})\n"
		f"👤 Тренер - {trainer_name}\n\n"
		f"{balance_line}"
		f"👥 Записано {bookings_count} из {max_participants}:\n"
	)

	for i, p in enumerate(participants, 1):
		username = f" @{p['username']}" if p.get('username') else ''
		caption += f"{i}) {p['full_name']}{username}\n"

	return caption
