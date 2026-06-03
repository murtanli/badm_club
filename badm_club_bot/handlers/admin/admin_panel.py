from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.admin_keyboards.admin_panel_inline import admin_panel_inline
from keyboards.admin_keyboards.check_stats_reports_inline import check_stats_reports_inline
from keyboards.admin_keyboards.create_broadcast_inline import create_broadcast_inline
from keyboards.admin_keyboards.manage_trainings_inline import manage_trinings_inline
from keyboards.admin_keyboards.manage_users_inline import manage_users_inline
from keyboards.admin_keyboards.club_settings_inline import club_settings_inline

router = Router(name=__name__)


@router.callback_query(F.data == "admin:menu")
async def check_schedule(callback: CallbackQuery ):
	await callback.message.edit_text("👋 С возвращением в АЛГАритм! Вы админ ! \n Выберите действие в меню ниже:", reply_markup=admin_panel_inline())
	await callback.answer()


@router.callback_query(F.data == "admin:trainings")
async def manage_training_panel_admin(callback: CallbackQuery):
	await callback.message.edit_text(
		text="Выберите действие",
		reply_markup=manage_trinings_inline()
	)
	await callback.answer()


@router.callback_query(F.data == "admin:users")
async def manage_users_panel_admin(callback: CallbackQuery):
	await callback.message.edit_text(
		text="Выберите действие",
		reply_markup=manage_users_inline()
	)
	await callback.answer()


@router.callback_query(F.data == "admin:stats")
async def check_stats_reports(callback: CallbackQuery):
	await callback.message.edit_text(
		text="Выберите действие",
		reply_markup=check_stats_reports_inline()
	)
	await callback.answer()


@router.callback_query(F.data == "admin:settings")
async def check_stats_reports(callback: CallbackQuery):
	await callback.message.edit_text(
		text="Выберите действие",
		reply_markup=club_settings_inline()
	)
	await callback.answer()


@router.callback_query(F.data == "admin:broadcast")
async def check_stats_reports(callback: CallbackQuery):
	await callback.message.edit_text(
		text="Выберите действие",
		reply_markup=create_broadcast_inline()
	)
	await callback.answer()