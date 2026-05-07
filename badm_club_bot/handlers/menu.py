from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.keyboard_start import main_menu_inline
from keyboards.keyboard_profile_inline import profile_inline
from keyboards.back_inline import back_inline
from keyboards.training_subs_inline import training_subs_inline
from keyboards.choose_schedule_inline import choose_schedule_inline

from services.api_client import get_profile, get_training_subs

import logging

from texts.profile_text import profile_text
from texts.common_text import ABOUT_BOT_TEXT, HELP_TEXT
from texts.balance_text import balance_text

logger = logging.getLogger("bot_menu")
router = Router(name=__name__)


@router.callback_query(F.data == "menu:schedule")
async def show_schedule(callback: CallbackQuery):
	await callback.message.edit_text("📅 Выберите действие:", reply_markup=choose_schedule_inline())
	await callback.answer()


@router.callback_query(F.data == "menu:profile")
async def show_profile(callback: CallbackQuery):
	profile_info = await get_profile(callback.from_user.id)
	sub_info = profile_info['subscription']
	if 'message' in sub_info:
		subs_stat = sub_info['message']
	else:
		subs_stat = (f"«{sub_info['name']}»: \n "
					 f"осталось {sub_info['remaining']} из {sub_info['total']} тренировок (куплен {sub_info['purchased_at']})")

	if profile_info['full_name']:
		text = profile_text(
			full_name=profile_info['full_name'],
			username=profile_info['username'],
			telegram_id=profile_info['telegram_id'],
			balance=profile_info['balance'],
			subscription_status=subs_stat,
			completed=0
		)
	else:
		text = "Профиль не найден. Зарегистрируйтесь /start"
	await callback.message.edit_text(text, reply_markup=profile_inline())
	await callback.answer()


@router.callback_query(F.data == "menu:balance")
async def show_balance(callback: CallbackQuery):
	sub = await get_training_subs(callback.from_user.id)
	text = balance_text(sub['balance'], sub['user_subscription'])
	await callback.message.edit_text(text, reply_markup=training_subs_inline(sub['available_subscriptions']))
	await callback.answer()


@router.callback_query(F.data == "menu:help")
async def show_help(callback: CallbackQuery):
	text = HELP_TEXT
	await callback.message.edit_text(text, reply_markup=back_inline())
	await callback.answer()


@router.callback_query(F.data == "menu:about")
async def show_about(callback: CallbackQuery):
	text = ABOUT_BOT_TEXT
	await callback.message.edit_text(text, reply_markup=back_inline())
	await callback.answer()


@router.callback_query(F.data == "menu:back")
async def back_to_start_menu(callback: CallbackQuery):
	await callback.message.edit_text(
		f"👋 С возвращением в BadmZone! \n Выберите действие в меню ниже:",
		reply_markup=main_menu_inline()
	)
