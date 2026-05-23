weekday_abbr = {
	"Понедельник": "ПН",
	"Вторник": "ВТ",
	"Среда": "СР",
	"Четверг": "ЧТ",
	"Пятница": "ПТ",
	"Суббота": "СБ",
	"Воскресенье": "ВС",
}


def get_occupancy_status(occupancy: int) -> str:
	if occupancy >= 90:
		return "🔴"
	elif occupancy >= 50:
		return "🟠"
	elif occupancy >= 10:
		return "🟡"
	else:
		return "🟢"


def training_button_text(
		type_name: str,
		date: str,
		time: str,
		weekday: str,
		max_participants: int,
		bookings_count: int,
		is_cancelled: bool) -> str:

	if len(type_name) > 19:
		type_name = f"{type_name[:19]}..."

	if is_cancelled:
		return f"❌ {date} {time} – отменена"

	if max_participants:
		occupancy = round((bookings_count / max_participants) * 100)
		fullness = f"{bookings_count}/{max_participants}"
	else:
		occupancy = 0
		fullness = "0/0"

	stat_emoji = get_occupancy_status(occupancy)
	weekday_short = weekday_abbr.get(weekday, weekday[:2])

	text = (
		f"{stat_emoji} {date} {weekday_short} {time} - {type_name} ({fullness})"
	)

	return text
