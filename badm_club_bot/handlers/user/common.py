from aiogram import Router, types, F
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards.keyboard_start import main_menu_inline

router = Router(name=__name__)


@router.message()
async def echo_message(message: types.Message):
	await message.answer(
		"Такой команды не существует 🤔\n"
		"Используйте /help, чтобы посмотреть доступные команды."
	)


@router.callback_query(F.data == "menu:back")
async def back_to_start_menu(callback: CallbackQuery, state: FSMContext):
	await state.clear()
	await callback.message.edit_text(
		f"👋 С возвращением в ALGArithm! \n Выберите действие в меню ниже:",
		reply_markup=main_menu_inline()
	)
