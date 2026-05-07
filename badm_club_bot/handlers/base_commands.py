from aiogram import Router, F
from aiogram.types import Message
from keyboards.keyboard_start import main_menu
from services.api_client import get_profile
from aiogram.fsm.context import FSMContext

router = Router(name=__name__)

@router.message(F.text == "👤 Профиль")
async def cmd_profile(message: Message):
    data = await get_profile(message.from_user.id)
    if data.get("full_name"):
        text = f"👤 Профиль\nИмя: {data['full_name']}\nБаланс: {data['balance']} руб."
    else:
        text = "Профиль не найден. Зарегистрируйтесь /start"
    await message.answer(text, reply_markup=main_menu())

@router.message(F.text == "💰 Баланс")
async def cmd_balance(message: Message):
    data = await get_profile(message.from_user.id)
    balance = data.get('balance', 0)
    await message.answer(f"💰 Ваш баланс: {balance} руб.", reply_markup=main_menu())

@router.message(F.text == "❓ Помощь")
async def cmd_help(message: Message):
    text = ("📋 Правила возврата средств:...")  # скопируй текст как в исходном боте
    await message.answer(text, reply_markup=main_menu())

@router.message(F.text == "ℹ️ О боте")
async def cmd_about(message: Message):
    text = "🤖 Бот для записи на бадминтон.\nПо вопросам: @admin"
    await message.answer(text, reply_markup=main_menu())