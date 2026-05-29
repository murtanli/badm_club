import asyncio
from datetime import datetime, time
from aiogram import Bot
from services.api_client import get_tomorrow_bookings

async def send_tomorrow_reminders(bot: Bot):
    bookings = await get_tomorrow_bookings()
    if not bookings:
        return

    user_bookings = {}
    for b in bookings:
        uid = b['telegram_id']
        user_bookings.setdefault(uid, []).append(b)

    for uid, items in user_bookings.items():
        text = "🔔 *Напоминание о завтрашних тренировках:*\n\n"
        for item in items:
            text += f"• {item['start_time']} – _{item['type_name']}_ ({item['gym_name']})\n"
        await bot.send_message(chat_id=uid, text=text, parse_mode='Markdown')
        await asyncio.sleep(0.5)

async def daily_reminder_loop(bot: Bot):
    """Запускает проверку каждый час, но отправляет только в 12:00"""
    last_sent_date = None
    while True:
        now = datetime.now()
        if time(12, 0) <= now.time() <= time(12, 5):
            if last_sent_date != now.date():
                await send_tomorrow_reminders(bot)
                last_sent_date = now.date()
        await asyncio.sleep(60)