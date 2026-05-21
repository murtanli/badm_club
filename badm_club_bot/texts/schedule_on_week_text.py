from aiogram.utils.markdown import hbold


def schedule_on_week_text(schedule_on_week_data: list) -> str:
	lines = ["📊 Участники на неделю:\n"]

	for data_on_day in schedule_on_week_data:
		lines.append(hbold(f"📅 {data_on_day['date']}"))
		for session in data_on_day['sessions']:
			gym_info = session['gym_name']
			if session.get('gym_short_address'):
				gym_info += f" ({session['gym_short_address']})"
			elif session.get('gym_address'):
				split_addr = session['gym_address'].split(',')
				short_addr = split_addr[0][:30]
				num_addr = split_addr[1]
				gym_info += f" ({short_addr},{num_addr})"

			lines.append(f"⏰ {session['time']} - {session['type_name']} ({gym_info})")

			participants = session['participants']
			if participants:
				for num, p in enumerate(participants, 1):
					username = f" (@{p['username']})" if p.get('username') else ''
					lines.append(f"  {num}. {p['full_name']}{username}")
			else:
				lines.append("  Пока никто не записался.")
			lines.append("")

	return "\n".join(lines)
