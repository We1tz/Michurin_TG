from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard_location = ReplyKeyboardMarkup(
    keyboard=[
        [
        KeyboardButton(text="🔎",
                        request_location = True)
        ]
    ]
)
