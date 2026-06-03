from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def manage_users_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🙍‍♂️ Список пользователей", callback_data="admin_user:create")],
        [InlineKeyboardButton(text="🔎 Поиск пользователя", callback_data="admin_user:create")],
        [InlineKeyboardButton(text="❌ Удалить пользователя", callback_data="admin_user:delete")],
        [InlineKeyboardButton(text="✏️ Редактировать пользователя", callback_data="admin_user:edit")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin:menu")],
    ])