from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def check_stats_reports_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 Популярность тренировок", callback_data="admin_stat:stats:popularity")],
        [InlineKeyboardButton(text="💵 Финансовый отчёт", callback_data="admin_stat:stats:finance")],
        [InlineKeyboardButton(text="👥 Активность пользователей", callback_data="admin_stat:stats:activity")],
        [InlineKeyboardButton(text="📅 Загруженность залов", callback_data="admin_stat:stats:halls")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin:menu")],
    ])