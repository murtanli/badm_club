from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def trainers_inline(trainers: list[dict]) -> InlineKeyboardMarkup:
    keyboard = []
    for trainer in trainers:
        keyboard.append([
            InlineKeyboardButton(
                text=trainer['name'],
                callback_data=f"trainer:{trainer['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text="📊Участники на неделю", callback_data="schedule:on_week_trainers")])
    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="menu:schedule")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def gyms_inline(gyms: list[dict]) -> InlineKeyboardMarkup:
    keyboard = []
    for gym in gyms:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{gym['name']} | {gym['address']}",
                callback_data=f"gym:{gym['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text="📊Участники на неделю", callback_data="schedule:on_week_gyms")])
    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="menu:schedule")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
