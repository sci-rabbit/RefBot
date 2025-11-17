import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from core.keyboards.main_kb import main_kb


logger = logging.getLogger()

start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    logger.info(
        "User %r start bot... \n ID: %r\nFirst Name: %r\nLast Name: %r",
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name,
    )
    await message.answer(
        "Привет! Выберите действие:",
        reply_markup=main_kb,
    )
