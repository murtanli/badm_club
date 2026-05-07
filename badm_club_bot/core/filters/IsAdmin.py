from aiogram import types
from aiogram.filters import BaseFilter


class IsAdmin(BaseFilter):
	async def __call__(self, message: types.Message) -> bool:
		role = await get_user_role(message.from_user.id)
		return role == "admin"