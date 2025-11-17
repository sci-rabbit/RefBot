from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔎Поиск"),
            KeyboardButton(text="🧠Предложка"),
        ],
    ],
    resize_keyboard=True,
)
