from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def club_settings_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏢 Залы", callback_data="admin_settings:halls")],
        [InlineKeyboardButton(text="👨‍🏫 Тренеры", callback_data="admin_settings:trainers")],
        [InlineKeyboardButton(text="🏷️ Типы тренировок", callback_data="admin_settings:training_types")],
        [InlineKeyboardButton(text="🎫 Абонементы", callback_data="admin_settings:subscriptions")],
        [InlineKeyboardButton(text="👥 Администраторы", callback_data="admin_settings:admins")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin:menu")],
    ])