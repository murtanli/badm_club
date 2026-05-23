from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext

from keyboards.booking_training_info import booking_training_info
from keyboards.trainers_gyms_inline import trainers_inline, gyms_inline
from keyboards.booking_training_inline import booking_training_inline

from services.api_client import get_gyms, get_trainers, get_sports_training, get_full_bookings_on_week, \
	get_session_data, get_trainer_photo_bytes

from texts.schedule_on_week_text import schedule_on_week_text

import logging

from texts.session_text import session_text
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
	not_available = False

	session_text_lines = session_text(
		data['type_name'],
		data.get('type_description', ''),
		data['weekday'],
		data['start_datetime'],
		data['end_datetime'],
		data['gym_name'],
		data['gym_address'],
		data['trainer_name'],
		float(data['cost']),
		data['user_balance'],
		data['bookings_count'],
		data['max_participants'],
		data['participants']
	)

	if data['max_participants'] == len(data['participants']):
		not_available = True

	inline_keyboard = booking_training_info(
		not_available,
		data['id'],
		float(data['user_balance']),
		float(data['cost']),
		data['user_subscription'],
		data['participants'],
		callback.from_user.id
	)

	try:
		await callback.message.delete()
	except TelegramBadRequest as e:
		logging.error(f"Не удалось удалить сообщение: {e}")

	photo_bytes = await get_trainer_photo_bytes(data.get('trainer'))
	if photo_bytes:
		from aiogram.types import BufferedInputFile
		photo_file = BufferedInputFile(photo_bytes, filename="trainer.jpg")
		await callback.bot.send_photo(
			chat_id=callback.message.chat.id,
			photo=photo_file,
			caption=session_text_lines,
			parse_mode='Markdown',
			reply_markup=inline_keyboard
		)
	else:
		await callback.bot.send_message(
			chat_id=callback.message.chat.id,
			text=session_text_lines,
			parse_mode='Markdown',
			reply_markup=inline_keyboard
		)
	await callback.answer()
