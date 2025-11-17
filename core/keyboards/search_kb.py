from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_inline_search_kb(count):
    search_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Показать ещё 👇",
                    callback_data=f"next:{count}",
                )
            ]
        ]
    )
    return search_kb
