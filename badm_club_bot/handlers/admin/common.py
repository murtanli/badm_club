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


