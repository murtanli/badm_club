import os
import aiohttp
from utils.config import API_TOKEN, API_BASE_URL
import logging

logger = logging.getLogger(__name__)


def _headers():
    return {"Authorization": f"Token {API_TOKEN}"}


async def get_profile(telegram_id: int):
    logger = logging.getLogger("api_client-get_profile")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{API_BASE_URL}/user/profile/{telegram_id}",
                    headers=_headers()
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    result = await response.json()
                    logger.error(f"Ошибка сервера ответ - {result}")
                    return False
    except Exception as e:
        logger.error(f"Ошибка бота - \n {e}")
        return False


async def get_training_subs(telegram_id: int):
    logger = logging.getLogger("api_client-get_training_subs")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{API_BASE_URL}/training-subscriptions/{telegram_id}",
                    headers=_headers()
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    result = await response.jsson()
                    logger.error(f"Ошибка сервера ответ - {result}")
                    return False
    except Exception as e:
        logger.error(f"Ошибка бота - \n {e}")
        return False


# async def get_profile(telegram_id: int):
#     async with aiohttp.ClientSession() as s:
#         async with s.get(f"{API_BASE_URL}/users/me/?telegram_id={telegram_id}", headers=_headers()) as resp:
#             return await resp.json()

async def check_registration(telegram_id: int):
    async with aiohttp.ClientSession() as s:
        payload = {"telegram_id": telegram_id}
        async with s.post(f"{API_BASE_URL}/auth/verify/", json=payload, headers=_headers()) as resp:
            return await resp.json()


async def register_user(telegram_id: int, full_name: str, phone: str, username: str = None):
    async with aiohttp.ClientSession() as s:
        payload = {"telegram_id": telegram_id, "full_name": full_name, "phone": phone, "username": username}
        async with s.post(f"{API_BASE_URL}/auth/register/", json=payload, headers=_headers()) as resp:
            return await resp.json()


async def get_gyms() -> list:
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{API_BASE_URL}/gyms/", headers=_headers()) as resp:
            data = await resp.json()
            return data.get('gyms', [])


async def get_trainers() -> list:
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{API_BASE_URL}/trainers/", headers=_headers()) as resp:
            data = await resp.json()
            return data.get('trainers', [])


async def get_sports_training(id: int, type: str) -> list:
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{API_BASE_URL}/sport_training_list/{type}/{id}", headers=_headers()) as resp:
            data = await resp.json()
            return data


async def get_full_bookings_on_week():
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{API_BASE_URL}/sport_training/full_bookings/", headers=_headers()) as resp:
            data = await resp.json()
            return data


async def get_session_data(session_id: int, telegram_id: int):
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{API_BASE_URL}/training/{session_id}/?telegram_id={telegram_id}",
                         headers=_headers()) as resp:
            data = await resp.json()
            return data


# УБРАТЬ ПОСЛЕ ДЕПЛОЯ И ИСПОЛЬЗОВАТЬ AIOGRAM ДЛЯ ВСТАВКИ ФОТО
async def get_trainer_photo_bytes(trainer_id: int) -> bytes | None:
    url = f"{API_BASE_URL}/sport_training/trainer-photo/{trainer_id}/"
    logger.info(f"Запрос фото: {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=_headers()) as resp:
            logger.info(f"Статус ответа фото: {resp.status}")
            if resp.status == 200:
                content_type = resp.headers.get('Content-Type', '')
                logger.info(f"Content-Type: {content_type}")
                data = await resp.read()
                logger.info(f"Размер фото: {len(data)} байт")
                return data
            else:
                text = await resp.text()
                logger.error(f"Ошибка получения фото: {resp.status} - {text}")
                return None


async def post_pay_sub_from_balance(
        telegram_id: int,
        subscription_id: int,
    ):
    url = f"{API_BASE_URL}/balance/pay_sub_from_balance/"
    json = {
        "telegram_id": telegram_id,
        "subscription_id": subscription_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url,json=json, headers=_headers()) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data
            else:
                logger.error(f"Ошибка покупки статус - {resp.status}| ответ - {resp.json()}")
                return await resp.json()


async def post_create_booking_from_subscription(telegram_id: int, training_id: int):
    url = f"{API_BASE_URL}/booking/create_booking_from_subscription/"
    payload = {
        "telegram_id": telegram_id,
        "training_id": training_id
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=_headers()) as resp:
                if resp.status in (200, 201):
                    data = await resp.json()
                    return {"success": True, **data}
                else:
                    error_text = await resp.text()
                    logger.error(f"Ошибка записи статус {resp.status}: {error_text}")
                    return {"success": False, "error": f"Ошибка сервера {resp.status}"}
        except Exception as e:
            logger.error(f"Исключение при вызове API: {e}", exc_info=True)
            return {"success": False, "error": "Сервис временно недоступен"}


async def post_cancel_booking(telegram_id: int, training_session_id: int):
    """
    Отменяет запись на тренировку через API.
    Возвращает словарь с ключами 'success' и 'message' (или 'error' при ошибке).
    """
    url = f"{API_BASE_URL}/booking/cancel"
    payload = {
        "telegram_id": telegram_id,
        "training_session_id": training_session_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=_headers()) as resp:
            if resp.status in (200, 201):
                data = await resp.json()
                return data
            else:
                error_text = await resp.text()
                logger.error(f"Ошибка отмены записи (статус {resp.status}): {error_text}")
                return {"success": False, "error": f"Ошибка сервера {resp.status}"}