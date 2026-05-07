from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.trainers_gyms_inline import trainers_inline, gyms_inline

from services.api_client import get_gyms, get_trainers

import logging

from texts.profile_text import profile_text
from texts.common_text import ABOUT_BOT_TEXT, HELP_TEXT
from texts.balance_text import balance_text

logger = logging.getLogger("bot_booking")
router = Router(name=__name__)


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
