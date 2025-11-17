from aiogram import Router

from views.search_view.search_view import search_router
from views.start_view.start_view import start_router
from views.suggestion_view.suggestion_view import suggestion_router


router = Router()


router.include_router(start_router)
router.include_router(suggestion_router)
router.include_router(search_router)
