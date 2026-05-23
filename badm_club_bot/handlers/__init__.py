__all__ = ("router",)

from aiogram import Router

from .start import router as start_router
from .common import router as common_router
from .menu import router as menu
from .profile_menu import router as profile_menu
from .booking import router as booking
from .top_up_balance import router as top_up_balance
from .booking_process import router as booking_process

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
