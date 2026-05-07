from aiogram import Router, flags
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from services.api_client import check_registration, register_user
from states.register_state import RegisterStates
import logging

from keyboards.keyboard_start import main_menu, main_menu_inline

router = Router(name=__name__)
logger = logging.getLogger("bot")


@router.message(Command("start"), flags={"dispatcher_only": True})
async def start_command(message: Message, state: FSMContext):
	await state.clear()
	auth_stat = await check_registration(message.from_user.id)
	if auth_stat['registered']:
		await message.answer(
			f"👋 С возвращением в BadmZone! \n Выберите действие в меню ниже:",
			reply_markup=main_menu_inline()
		)
	else:
		await message.answer(
			f"👋 Добро пожаловать в BadmZone! Давайте познакомимся! \n 📝 Пожалуйста, введите вашу фамилию и имя:",
		)
		await state.set_state(RegisterStates.waiting_for_fio)


@router.message(RegisterStates.waiting_for_fio)
async def get_fio(message: Message, state: FSMContext):
	await message.answer(
		f"📞 Теперь введите ваш номер телефона:",
	)
	fio = message.text
	await state.update_data(fio=fio)
	await state.set_state(RegisterStates.waiting_for_num_phone)


@router.message(RegisterStates.waiting_for_num_phone)
async def get_num_phone(message: Message, state: FSMContext):
	data = await state.get_data()
	num_phone = message.text
	fio = data.get('fio')

	register_stat = await register_user(
		message.from_user.id,
		fio,
		num_phone,
		message.from_user.username)

	if register_stat:
		logging.info("save data !")
		await message.answer(
			f"✅ Спасибо! Регистрация завершена!",
			reply_markup=main_menu()
		)
	else:
		await message.answer(
			f"Регистрация не завершена, ошибка \n обратитесь к администратору",
			reply_markup=main_menu()
		)
	await state.clear()
