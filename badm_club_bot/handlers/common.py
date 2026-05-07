from aiogram import Router, types
from aiogram.enums import ChatAction

router = Router(name=__name__)


@router.message()
async def echo_message(message: types.Message):
    await message.answer(
        "Такой команды не существует 🤔\n"
        "Используйте /help, чтобы посмотреть доступные команды."
    )
