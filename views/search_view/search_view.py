import structlog
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import settings
from core.db.database import get_session
from core.states.search_state import SearchStates
from views.search_view.handlers import send_results


logger = structlog.getLogger(__name__)

search_router = Router()


@search_router.message(F.text == "🔎Поиск")
async def search_view(
    message: Message,
    state: FSMContext,
):
    await state.set_state(SearchStates.waiting_for_query)
    logger.info(
        "Состояние SearchState было установлено, Ожидание текста от пользователя",
        user_id=message.from_user.id,
    )
    await message.answer("Введите запрос для поиска 🔍")


@search_router.message(SearchStates.waiting_for_query)
async def process_search(message: Message, state: FSMContext):
    query = message.text
    await state.update_data(waiting_for_query=query)
    logger.info("SearchState updated", waiting_for_query=query)

    if not query.startswith("#"):
        await message.answer("❌ Правильный запрос: #<слово1> #<слово2>...")
        return

    await state.set_state(SearchStates.albums)

    async with get_session() as session:
        await send_results(
            bot=message.bot,
            session=session,
            search=query,
            message=message,
            state=state,
            offset=0,
            page_size=settings.search.page_size,
        )


@search_router.callback_query(
    F.data.startswith("next:"),
    SearchStates.albums,
)
async def next_page_handler(callback: CallbackQuery, state: FSMContext):
    _, offset_str = callback.data.split(":")
    offset = int(offset_str)

    state_data = await state.get_data()
    search = state_data.get("waiting_for_query")
    if not search:
        await callback.answer("❌ Невозможно продолжить — запрос не найден.")
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("Загружаю следующую страницу...")

    async with get_session() as session:
        await send_results(
            bot=callback.bot,
            session=session,
            search=search,
            message=callback.message,
            state=state,
            offset=offset,
            page_size=settings.search.page_size,
        )
