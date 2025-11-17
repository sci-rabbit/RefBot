import asyncio
import json
import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from auth.check_admin import IsAdmin, send_notification_to_admin
from core.keyboards.main_kb import main_kb
from core.keyboards.suggestion_kb import suggestion_reply_kb, get_inline_publish_kb
from redis_client.redis import AsyncRedisClient
from src.bot import bot
from core.states.suggestion_state import SuggestionStates
from views.suggestion_view.utils import collect_media, process_state_photo

logger = logging.getLogger(__name__)

suggestion_router = Router()


@suggestion_router.message(F.text == "Назад")
async def suggest_back(
    message: Message,
):
    await message.answer(
        text="Главное меню:",
        reply_markup=main_kb,
    )
    logger.info(
        "[Назад] Пользователь %r вернулся в меню.",
        message.from_user.id,
    )


@suggestion_router.message(F.text == "🧠Предложка")
async def suggestion_view(message: Message):
    await message.answer(
        text="Выберите действие:",
        reply_markup=suggestion_reply_kb,
    )
    logger.info(
        "[Предложка] Пользователь %r открыл меню предложки.",
        message.from_user.id,
    )


@suggestion_router.message(F.text == "Добавить")
async def suggest_add(
    message: Message,
    state: FSMContext,
):
    await state.set_state(SuggestionStates.waiting_for_photos)
    await message.answer("Отправь ваши фото для предложки 💬")
    logger.info(
        "[Добавить] Пользователь %r начал добавление фото.",
        message.from_user.id,
    )


@suggestion_router.message(F.text == "Просмотр", IsAdmin())
async def suggest_view(
    message: Message,
):
    redis = await AsyncRedisClient.get_client()

    keys = await redis.keys("suggestion:*")
    if not keys:
        await message.answer("📭 Нет предложенных фото для просмотра.")
        logger.info(
            "[Просмотр] Админ %r: нет данных.",
            message.from_user.id,
        )
        return

    for key in keys:
        data = await redis.get(key)
        if not data:
            continue

        media = collect_media(data)

        await message.answer_media_group(media=media)

        await message.answer(
            "Действия с этой подборкой:",
            reply_markup=get_inline_publish_kb(key),
        )
        logger.info(
            "[Просмотр] Админ %r просмотрел %r.",
            message.from_user.id,
            key,
        )


@suggestion_router.callback_query(F.data.startswith("publish_"))
async def handle_view_publish(
    callback: CallbackQuery,
):
    _, key = callback.data.split("_")

    redis = await AsyncRedisClient.get_client()
    data = await redis.get(key)
    if not data:
        await callback.answer("❌ Ошибка: данные не найдены.")
        logger.warning("[Publish] Не найдены данные по ключу %r.", key)
        return

    media = collect_media(data)
    await bot.send_media_group(chat_id=-1002704717403, media=media)

    await redis.delete(key)

    await callback.message.edit_reply_markup()
    await callback.answer("Пост успешно опубликован")
    logger.info(
        "[Publish] Админ %r опубликовал %r.",
        callback.from_user.id,
        key,
    )


@suggestion_router.callback_query(F.data.startswith("delete_"))
async def handle_view_delete(
    callback: CallbackQuery,
):
    _, key = callback.data.split("_")

    redis = await AsyncRedisClient.get_client()
    await redis.delete(key)

    await callback.message.edit_reply_markup()
    await callback.answer("Данные очищены")
    logger.info(
        "[Delete] Админ %r удалил %r.",
        callback.from_user.id,
        key,
    )


@suggestion_router.message(SuggestionStates.waiting_for_photos)
async def process_suggestion(
    message: Message,
    state: FSMContext,
):
    if not (message.photo or message.document):
        return

    redis = await AsyncRedisClient.get_client()

    media_group, objects = await process_state_photo(message, state)

    if message.media_group_id:
        media_group["group_id"] = message.media_group_id
        await state.update_data(waiting_for_photos=media_group)

        await redis.set(f"suggestion:{message.media_group_id}", json.dumps(media_group))
        logger.info(
            "[Suggest] Получена медиагруппа %r от %r",
            message.media_group_id,
            message.from_user.id,
        )

        await asyncio.sleep(1)
        data_after = await state.get_data()
        current = data_after.get("waiting_for_photos", {})

        if len(current.get("photos", [])) == len(objects):
            await message.answer(
                f"✅ Получено фото из медиагруппы {len(objects)} фото\n"
                f"📝 Подпись: {media_group.get('caption') or '—'}"
            )
            await send_notification_to_admin(
                bot,
                redis,
            )
            await state.clear()

        if len(current.get("documents", [])) == len(objects):
            await message.answer(
                f"✅ Получено фото из медиагруппы {len(objects)} фото\n"
                f"📝 Подпись: {media_group.get('caption') or '—'}"
            )
            await send_notification_to_admin(
                bot,
                redis,
            )
            await state.clear()

        return

    await state.update_data(waiting_for_photos=media_group, done=True)
    await state.clear()
    await message.answer(
        f"✅ Получено одиночное фото\n"
        f"📝 Подпись: {media_group.get('caption') or '—'}"
    )

    await redis.set(f"suggestion:{message.message_id}", json.dumps(media_group))
    logger.info(
        "[Suggest] Получено одиночное фото %r от %r",
        message.message_id,
        message.from_user.id,
    )

    await send_notification_to_admin(bot, redis)
