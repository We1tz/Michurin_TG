from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard_location = ReplyKeyboardMarkup(
    keyboard=[
        [

        KeyboardButton(text="🔎",
                        resize_keyboard = True,
                        request_location = True)
        ]
    ]
)
