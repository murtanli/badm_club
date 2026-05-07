from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def trainers_inline(trainers: list) -> InlineKeyboardMarkup:
    keyboard = []
    for trainer in trainers:
        keyboard.append([
            InlineKeyboardButton(
                text=trainer['name'],
                callback_data=f"trainer:{trainer['id']}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)