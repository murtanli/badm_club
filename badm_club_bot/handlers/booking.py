from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext
from keyboards.trainers_gyms_inline import trainers_inline, gyms_inline
from keyboards.booking_training_inline import booking_training_inline

from services.api_client import get_gyms, get_trainers, get_sports_training, get_full_bookings_on_week, \
    get_session_data, get_trainer_photo_bytes

from texts.schedule_on_week_text import schedule_on_week_text

import logging

from utils.config import API_BASE_URL

logger = logging.getLogger("bot_booking")
router = Router(name=__name__)


# Обработка кнопок выбора тренировок по трениру или по залам
# для отображеия списка трениров и залов

@router.callback_query(F.data == "schedule:sports_gyms")
async def show_gyms(callback: CallbackQuery):
    gyms = await get_gyms()
    gyms_inline_data = gyms_inline(gyms)
    text = (
        "🏢 Выберите зал:"
    )
    await callback.message.edit_text(text, reply_markup=gyms_inline_data)
    await callback.answer()


@router.callback_query(F.data == "schedule:sports_trainers")
async def show_trainers(callback: CallbackQuery):
    trainers = await get_trainers()
    trainers_inline_data = trainers_inline(trainers)
    text = (
        "🏢 Выберите тренера:"
    )
    await callback.message.edit_text(text, reply_markup=trainers_inline_data)
    await callback.answer()


@router.callback_query(F.data == "schedule:on_week_trainers")
async def show_all_bookings(callback: CallbackQuery):
    schedule_on_week_data = await get_full_bookings_on_week()
    text = schedule_on_week_text(schedule_on_week_data)
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад к выбору тип записи", callback_data="menu:schedule")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:back")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=inline_keyboard)


# Отображение списков тренировок по залу и по тренеру
# Берется айди тренира либо зала

@router.callback_query(F.data.startswith("trainer:trainer_booking-"))
async def process_trainer_choice(callback: CallbackQuery):
    trainer_id = int(callback.data.split("-")[1])

    sport_list = await get_sports_training(trainer_id, "trainer")

    keyboard_inline_data = booking_training_inline(sport_list, "schedule:sports_trainers")

    count_filled = 0
    for training in sport_list:
        if int(training['max_participants']) == int(training['bookings_count']):
            count_filled += 1

    text = (
        f"🏋️ Тренер:{sport_list[0]['trainer_name']}\n"
        f"📊 {len(sport_list)} тренировок, заполнено: {count_filled}\n"
        "📅 Выберите тренировку:"
    )

    await callback.message.edit_text(text, reply_markup=keyboard_inline_data)
    await callback.answer()


@router.callback_query(F.data.startswith("gym:gym_booking-"))
async def process_gym_choice(callback: CallbackQuery):
    gym_id = int(callback.data.split("-")[-1])

    sport_list = await get_sports_training(gym_id, "gym")

    keyboard_inline_data = booking_training_inline(sport_list, "schedule:sports_gyms")

    count_filled = 0
    for training in sport_list:
        if int(training['max_participants']) == int(training['bookings_count']):
            count_filled += 1

    text = (
        f"🏢 Зал:{sport_list[0]['gym_name'][0]} ({sport_list[0]['gym_name'][1]})\n"
        f"📊 {len(sport_list)} тренировок, заполнено: {count_filled}\n"
        "📅 Выберите тренировку:"
    )

    await callback.message.edit_text(text, reply_markup=keyboard_inline_data)
    await callback.answer()



@router.callback_query(F.data.startswith("training_session:id-"))
async def send_training_info(callback: CallbackQuery):
    training_session = int(callback.data.split("-")[-1])
    data = await get_session_data(training_session, callback.from_user.id)

    caption = (
        f"*{data['type_name']}*\n"
        f"{data.get('type_description', '')}\n\n"
        f"🗓 {data['weekday']}, {data['start_datetime']}\n"
        f"📍 {data['gym_name']} ({data['gym_address']})\n"
        f"👤 Тренер - {data['trainer_name']}\n\n"
        f"💳 Стоимость: {data['cost']} ₽ (баланс {data['user_balance']} ₽)\n"
        f"👥 Записано {data['bookings_count']} из {data['max_participants']}:\n"
    )
    for i, p in enumerate(data['participants'], 1):
        username = f" @{p['username']}" if p.get('username') else ''
        caption += f"{i}) {p['full_name']}{username}\n"

    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="menu:balance")],
            [InlineKeyboardButton(text="❓ Правила отмены", callback_data="menu:help")],
            [InlineKeyboardButton(text="◀️ Назад к выбору тип записи", callback_data="menu:schedule")],
        ]
    )

    # Удаляем исходное сообщение с кнопкой
    await callback.message.delete()

    # Получаем фото тренера (используем trainer_id из данных)
    photo_bytes = await get_trainer_photo_bytes(data.get('trainer'))
    if photo_bytes:
        from aiogram.types import BufferedInputFile
        photo_file = BufferedInputFile(photo_bytes, filename="trainer.jpg")
        await callback.bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=photo_file,
            caption=caption,
            parse_mode='Markdown',
            reply_markup=inline_keyboard
        )
    else:
        await callback.bot.send_message(
            chat_id=callback.message.chat.id,
            text=caption,
            parse_mode='Markdown',
            reply_markup=inline_keyboard
        )
    await callback.answer()