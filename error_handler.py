import structlog
from aiogram import types, Dispatcher
from aiogram.types import ErrorEvent
from sqlalchemy.exc import DatabaseError

logger = structlog.getLogger(__name__)


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

    if isinstance(exception, DatabaseError):
        logger.exception(
            "⚠️ Непредвиденная ошибка базы данных",
            event=event.update,
            user=user,
            error=str(exception),
            exc_info=True,
        )
    else:
        logger.exception(
            "⚠️ Ошибка при обработке:",
            event=event.update,
            user=user,
            error=str(exception),
            exc_info=True,
        )

    try:
        if message:
            await message.answer("⚠️ Внутренняя ошибка, попробуйте позже.")
        elif callback:
            await callback.answer("⚠️ Ошибка при выполнении запроса.", show_alert=True)
    except Exception as e:
        logger.warning(
            "Не удалось отправить сообщение об ошибке", error=str(e), exc_info=True
        )

    return True


def register_error_handlers(dp: Dispatcher):
    dp.errors.register(global_error_handler)


def setup_async_exception_handler(loop):
    def handle_exception(loop, context):
        msg = context.get("exception", context["message"])
        logger.error(
            "💥 Непойманное async-исключение",
            msg=msg,
            exc_info=context.get("exception"),
        )

    loop.set_exception_handler(handle_exception)
