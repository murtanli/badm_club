from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_panel_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Управление тренировками", callback_data="admin:trainings")],
        [InlineKeyboardButton(text="👥 Управление пользователями", callback_data="admin:users")],
        [InlineKeyboardButton(text="📊 Статистика и отчеты", callback_data="admin:stats")],
        [InlineKeyboardButton(text="⚙️ Настройки клуба", callback_data="admin:settings")],
        [InlineKeyboardButton(text="📢 Сделать объявление", callback_data="admin:broadcast")],
    ])