import logging
from aiogram import types, Dispatcher
from aiogram.types import ErrorEvent

logger = logging.getLogger(__name__)


async def global_error_handler(event: ErrorEvent):
    exception = event.exception
    user = None
    message = None
    callback = None

    if isinstance(event.update, types.Message):
        message = event.update
        user = message.from_user
    elif isinstance(event.update, types.CallbackQuery):
        callback = event.update
        user = callback.from_user

    logger.exception(
        "⚠️ Ошибка при обработке event=%r от пользователя=%r: %s",
        event.update,
        user,
        exception,
    )

    try:
        if message:
            await message.answer("⚠️ Внутренняя ошибка, попробуйте позже.")
        elif callback:
            await callback.answer("⚠️ Ошибка при выполнении запроса.", show_alert=True)
    except Exception as e:
        logger.warning("Не удалось отправить сообщение об ошибке: %s", e)

    return True


def register_error_handlers(dp: Dispatcher):
    dp.errors.register(global_error_handler)


def setup_async_exception_handler(loop):
    def handle_exception(loop, context):
        msg = context.get("exception", context["message"])
        logging.error(
            f"💥 Непойманное async-исключение: {msg}", exc_info=context.get("exception")
        )

    loop.set_exception_handler(handle_exception)
