from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.trainers_gyms_inline import trainers_inline, gyms_inline
from keyboards.booking_training_inline import booking_training_inline

from services.api_client import get_gyms, get_trainers, get_sports_training

import logging

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


@router.callback_query(F.data == "schedule:on_week_trainers")
async def show_week_trainers(callback: CallbackQuery):
	# await callback.message.edit_text("📊 Список участников по тренерам за неделю (пока не реализовано)",
	# 								 reply_markup=back_to_schedule_keyboard())

	await callback.message.edit_text("fdf")
	await callback.answer()


@router.callback_query(F.data == "schedule:on_week_gyms")
async def show_week_gyms(callback: CallbackQuery):
	# await callback.message.edit_text("📊 Список участников по залам за неделю (пока не реализовано)",
	# 								 reply_markup=back_to_schedule_keyboard())
	await callback.message.edit_text("fdf")
	await callback.answer()
