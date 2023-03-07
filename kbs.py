from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton

links_kb = InlineKeyboardMarkup(row_width=1)
buttons = [
    InlineKeyboardButton(text="Местонахождение товара", callback_data="product_location"),
    InlineKeyboardButton(text="На сайт", url=r"https://asia-shadrin.ru"),
    InlineKeyboardButton(text="Группа в телеграмме", url=r"https://t.me/shadrin_china"),
    InlineKeyboardButton(text="Написать на Whatsapp", url=r"https://wa.me/79779773276")
]

links_kb.add(*buttons)