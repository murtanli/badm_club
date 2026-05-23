import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.back_inline import back_inline
from services.api_client import get_training_subs, post_pay_sub_from_balance, post_create_booking_from_subscription

from keyboards.back_inline import back_inline
from keyboards.booking_process_inline import booking_process_inline

router = Router(name=__name__)
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("buy_subscription:id-"))
async def buy_training_subscriptions(callback: CallbackQuery):
    subscription_id = int(callback.data.split("-")[-1])
    data = await get_training_subs(callback.from_user.id)

    enough_money = True
    sub_info = None
    for sub in data["available_subscriptions"]:
        if sub["id"] == subscription_id:
            sub_info = sub
            break

    if not sub_info:
        await callback.message.answer("❌ Абонемент не найден")
        await callback.answer()
        return

    price = float(sub_info["price"])
    balance = data["balance"]

    if price > balance:
        enough_money = False

    inline_keyboard = booking_process_inline(enough_money, price, subscription_id)

    text = (
        f"🎫 *{sub_info['name']}*\n"
        f"💰 Стоимость: {price:.1f} руб.\n"
        f"💳 Ваш баланс: {balance:.1f} руб.\n\n"
        "Выберите способ оплаты:"
    )

    await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=inline_keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("balance:pay_from_balance-"))
async def pay_from_balance(callback: CallbackQuery):
    subscription_id = int(callback.data.split("-")[-1])
    user_id = callback.from_user.id

    result = await post_pay_sub_from_balance(user_id, subscription_id)
    inline_keyboard = back_inline()
    if result.get("success"):
        new_balance = result.get("new_balance", 0)
        text = f"✅ Оплата прошла успешно!\n💰 Новый баланс: {new_balance:.2f} руб."
        await callback.message.edit_text(text, reply_markup=inline_keyboard)
    else:
        error_msg = result.get("error", "Неизвестная ошибка")
        text = f"❌ Ошибка при оплате: {error_msg}\nПопробуйте позже или обратитесь к администратору."

        await callback.message.edit_text(text, reply_markup=inline_keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("create_booking:subscription-"))
async def create_booking_from_subscription(callback: CallbackQuery):
    training_id = int(callback.data.split("-")[-1])
    user_id = callback.from_user.id

    await callback.message.delete()

    loading_msg = await callback.message.answer("⏳ Проверяем возможность записи...")

    result = await post_create_booking_from_subscription(user_id, training_id)

    await loading_msg.delete()

    if result.get("success"):
        remaining = result.get("remaining_trainings", 0)
        text = (
            f"✅ Вы успешно записаны на тренировку!\n"
            f"🎟 Осталось тренировок по абонементу: {remaining}"
        )
        await callback.message.answer(text, reply_markup=back_inline())
    else:
        error_msg = result.get("error", "Неизвестная ошибка")
        text = f"❌ Не удалось записаться: {error_msg}"
        await callback.message.answer(text, reply_markup=back_inline("menu:schedule"))

    await callback.answer()