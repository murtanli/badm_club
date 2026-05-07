__all__ = ("router",)

from aiogram import Router

from .start import router as start_router
from .common import router as common_router
from .base_commands import router as base_commands
from .menu import router as menu
from .profile_menu import router as profile_menu
router = Router(name=__name__)

router.include_routers(
    start_router,
    menu,
    profile_menu,
    base_commands,
)

# this one has to be the last!
router.include_router(common_router)