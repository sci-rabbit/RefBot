from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

suggestion_reply_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Просмотр"),
            KeyboardButton(text="Добавить"),
        ],
        [
            KeyboardButton(text="Назад"),
        ],
    ],
    resize_keyboard=True,
)


def get_inline_publish_kb(key):
    publish_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Опубликовать", callback_data=f"publish_{key}"
                ),
            ],
            [
                InlineKeyboardButton(text="🗑 Отмена", callback_data=f"delete_{key}"),
            ],
        ]
    )
    return publish_keyboard
