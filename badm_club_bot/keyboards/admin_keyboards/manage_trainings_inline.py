from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def manage_trinings_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎾 Создать новую тренировку", callback_data="admin_training:create")],
        [InlineKeyboardButton(text="🗓️ Создать расписание на неделю", callback_data="admin_training:create_on_week")],
        [InlineKeyboardButton(text="❌ Удалить тренировку", callback_data="admin_training:delete")],
        [InlineKeyboardButton(text="✏️ Редактировать тренировку", callback_data="admin_training:edit")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin:menu")],
    ])