__all__ = ("router",)

from aiogram import Router

from handlers.user.start import router as start_router
from handlers.user.common import router as common_router
from handlers.user.menu import router as menu
from handlers.user.profile_menu import router as profile_menu
from handlers.user.booking import router as booking
from handlers.user.top_up_balance import router as top_up_balance
from handlers.user.booking_process import router as booking_process

router = Router(name=__name__)

router.include_routers(
	start_router,
	menu,
	profile_menu,
	booking,
	top_up_balance,
	booking_process
)

router.include_router(common_router)
