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