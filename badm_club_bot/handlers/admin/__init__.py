__all__ = ("router",)

from aiogram import Router

from handlers.admin.common import router as common_router_admin
from handlers.admin.admin_panel import router as admin_panel

router = Router(name=__name__)

router.include_routers(
	admin_panel
)

router.include_router(common_router_admin)
