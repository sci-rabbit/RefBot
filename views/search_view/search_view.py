import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import settings
from core.states.search_state import SearchStates
from src.bot import bot
from src.tg_client import tg_client
from views.search_view.handlers import send_results, search_message_processor

logger = logging.getLogger(__name__)


search_router = Router()


@search_router.message(F.text == "🔎Поиск")
async def search_view(
    message: Message,
    state: FSMContext,
):
    await state.set_state(SearchStates.waiting_for_query)
    logger.info(
        "Состояние SearchState было установлено, Ожидание текста от пользователя user_id=%r",
        message.from_user.id,
    )
    await message.answer("Введите запрос для поиска 🔍")


@search_router.message(SearchStates.waiting_for_query)
async def process_search(
    message: Message,
    state: FSMContext,
):
    await state.update_data(waiting_for_query=message.text)
    logger.info(
        "Данные SearchState были обновлены, waiting_for_query=%r",
        message.text,
    )
    if not message.text.startswith("#"):
        await message.answer("❌ Правильный запрос: #<слово1> #<слово2>...")
        return

    state_data = await state.get_data()
    logger.info(
        "SearchState завершено",
    )

    search = state_data.get("waiting_for_query")
    logger.info(
        "SearchState.waiting_for_query=%r",
        search,
    )

    albums = await search_message_processor(
        tg_client,
        search,
        settings.limit,
        offset_id=0,
    )
    await state.set_state(SearchStates.albums)
    await state.update_data(albums=albums)

    await send_results(
        bot,
        albums,
        message,
    )


@search_router.callback_query(
    F.data.startswith("next:"),
    SearchStates.albums,
)
async def next_page_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    _, count = callback.data.split(":")

    state_data = await state.get_data()
    albums = state_data.get("albums")

    logger.info(
        "Обработка новой страницы count=%r",
        count,
    )

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.answer("Загружаю следующую страницу...")
    await send_results(
        bot,
        albums,
        callback.message,
        state,
        int(count),
    )
