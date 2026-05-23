import logging

from aiogram import Router, F
from aiogram.fsm import state
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message

from keyboards.back_inline import back_inline
from states.top_up_balance_state import Top_up_balance

logger = logging.getLogger("bot_booking")
router = Router(name=__name__)


@router.callback_query(F.data == "balance:top_up_balance")
async def top_up_balance(callback: CallbackQuery, state: FSMContext):
	inline_keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton(text="❌ Отмена", callback_data="menu:back")]
		]
	)
	await callback.message.edit_text(
		"💳 Пополнение баланса \n Введите сумму для пополнения (в рублях): \n Пример: 1000",
		reply_markup=inline_keyboard
	)
	await state.set_state(Top_up_balance.waiting_for_balance_amount)


@router.message(Top_up_balance.waiting_for_balance_amount)
async def get_balance_amount(message: Message, state: FSMContext):
	balance_amount = message.text
	# Проверка, что введено число
	if not balance_amount.isdigit():
		await message.answer("❌ Пожалуйста, введите число (только цифры).")
		return

	await state.update_data(balance_amount=int(balance_amount))
	data = await state.get_data()
	amount = data['balance_amount']

	text = (f"💳 Ссылка для оплаты {amount} руб.\n"
			"➡️ Перейдите по ссылке ниже для оплаты.)\n"
			"✅ Платеж проверяется автоматически - как только вы оплатите, баланс пополнится сам.\n"
			f"📋 Payment ID: `31a0fbd8-000f-5001-8000-15b112b2ac2d`\n\n"
			""
			"⚠️ Совет: После оплаты можете просто подождать ~30 секунд. Баланс обновится автоматически!"
			)

	inline_keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton(text="💳 Оплатить", callback_data="balance:confirm")],
			[InlineKeyboardButton(text="🔄 Проверить статус", callback_data="balance:status_check")],
			[InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:back")]
		]
	)
	await message.answer(text, reply_markup=inline_keyboard)
	await state.set_state(Top_up_balance.waiting_for_confirm)  # новое состояние


@router.callback_query(Top_up_balance.waiting_for_confirm, F.data == "balance:confirm")
async def confirm_top_up(callback: CallbackQuery, state: FSMContext):
	data = await state.get_data()
	amount = data['balance_amount']
	# Здесь логика отправки запроса на пополнение (например, создание платежа)
	await callback.message.edit_text(f"✅ Запрос на пополнение {amount}₽ отправлен. Ожидайте.", reply_markup=back_inline())
	await state.clear()
	await callback.answer()
