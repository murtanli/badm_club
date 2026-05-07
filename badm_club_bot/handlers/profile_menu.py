from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.keyboard_start import main_menu_inline
from keyboards.buy_subscription_inline import subscriptions_inline
import logging

logger = logging.getLogger("bot_profile_menu")
router = Router(name=__name__)


@router.callback_query(F.data == "profile:buy_subscription")
async def buy_subscription(callback: CallbackQuery):
	markup = await subscriptions_inline(callback.message.from_user.id)
	await callback.message.edit_text(
		f"🎫 Покупка абонемента в зал Бустан \n Выберите количество тренировок:",
		reply_markup=markup
	)


@router.callback_query(F.data == "profile:back")
async def back(callback: CallbackQuery):
	await callback.message.edit_text(
		f"👋 С возвращением в BadmZone! \n Выберите действие в меню ниже:",
		reply_markup=main_menu_inline()
	)

