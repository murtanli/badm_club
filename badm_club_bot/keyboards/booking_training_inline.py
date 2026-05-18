from decimal import Decimal

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from texts.training_button_text import training_button_text

import logging
logger = logging.getLogger("bot_booking_training")


def booking_training_inline(training_list: list[dict], callback_type: str) -> InlineKeyboardMarkup:
    keyboard = []

    for training in training_list:
        date, time = training['start_datetime'].split(" ")
        date = date.split(".")

        button_text = training_button_text(
            training['type_name'],
            f"{date[0]}.{date[1]}",
            time,
            training['weekday'],
            training['max_participants'],
            training['bookings_count'],
            training['is_cancelled']
        )

        keyboard.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"buy_subscription:{training['id']}"
            )
        ])

    keyboard.append([InlineKeyboardButton(text="◀️ Назад к тренерам", callback_data=f"{callback_type}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)