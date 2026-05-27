from collections import defaultdict
from decimal import Decimal
from aiogram.utils.markdown import hbold

def format_profile_bookings(bookings):
    if not bookings:
        return "У вас нет активных записей."

    grouped = defaultdict(list)
    for b in bookings:
        date_short = b['start_datetime'].split()[0]  # "26.05.2026" -> "26.05.2026"
        # лучше взять день.месяц: date_short = '.'.join(date_short.split('.')[:2])
        grouped[date_short].append(b)

    lines = []
    for date, items in sorted(grouped.items()):
        lines.append(f"📅 {date}")
        for item in items:
            time = item['start_datetime'].split()[1][:5]  # "12:00"
            title = item['training_name']
            if len(title) > 25:
                title = title[:22] + "..."
            lines.append(f"  ⏰ {time} – {title} ({item['gym_name']})")
    return "\n".join(lines)


def profile_text(full_name: str,
				 username: str,
				 telegram_id: int,
				 balance: float,
				 subscription_status: str,
				 completed: int,
				 active_bookings: list | None) -> str:
	balance = Decimal(balance)
	lines = [
		"👤 *Профиль пользователя*",
		"",
		f"*Имя:* {full_name}",
		f"*Username:* @{username}",
		f"*ID:* `{telegram_id}`",
		f"💳 *Баланс: {balance:.2f} руб.*",
		"",
		f"🎫 *Абонемент: {subscription_status}*",
		"",
		"📊 *Статистика тренировок:*",
		f"• Всего завершено: {completed}",
		"",
		"*Активные записи:*",
	]
	booking = format_profile_bookings(active_bookings)
	lines.append(booking)
	return "\n".join(lines)
