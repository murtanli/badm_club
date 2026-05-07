import os
import aiohttp
from utils.config import API_TOKEN, API_BASE_URL
import logging

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

async def get_subscriptions(telegram_id: int) -> list:
    """В будущем замени на запрос к DRF"""
    # Пока возвращаем тестовые данные
    return [
        {"id": 1, "name": "Дневной безлимит", "price": 500, "duration": "7 дней"},
        {"id": 2, "name": "Вечерний", "price": 700, "duration": "14 дней"},
    ]