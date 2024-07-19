from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="меню"), KeyboardButton(text="заказать блюда")], [KeyboardButton(text="заказать места")]],resize_keyboard=True)


credentials = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="отправить номер телефона", request_contact=True)]], resize_keyboard=True)

