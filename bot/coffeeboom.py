import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart

import os
import sys

import django
from asgiref.sync import sync_to_async


sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()


from botAdmin.models import TelegramUser, ChatMessage, EventData
from markups import menu, credentials

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.magic_data import MagicData
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("tg_token")


bot = Bot(token=TOKEN)
dp = Dispatcher()


class Ism(StatesGroup):
    ism = State()
    

from filters import helloFilter

@dp.message(CommandStart())
async def send_welcome(message: types.Message, hello):
    
    user = message.from_user
    
    
    
    user, created = await sync_to_async(TelegramUser.objects.get_or_create, thread_sensitive=True)(
        username=user.username,
        
        id_user=user.id,
        )
    if user.phone_number:
        await message.answer(f"Здравствуйте {user.name}", reply_markup=menu)
    else:
        await message.answer(f"Здравствуйте {user.username}, пожалуйста, отправьте ваш номер телефона", reply_markup=credentials, show_alert=False)


@dp.message(F.content_type == "contact")
async def send_welcome(message: types.Message, state: FSMContext):
    
    await state.set_state(Ism.ism)
    
    
    @sync_to_async
    def user_operations():
        user = TelegramUser.objects.get(
            id_user =message.from_user.id    
            )

        user.phone_number = message.contact.phone_number
        user.save()
    
    await user_operations()
    
    await message.answer(f"Как мне вас назвать?")



@dp.message(Ism.ism)
async def send_welcome(message: types.Message, state: FSMContext):
    
    await state.clear()

    
    @sync_to_async
    def user_operations():
        user = TelegramUser.objects.get(
            id_user =message.from_user.id    
            )
        user.name = message.text
        user.save()
        return user
    user = await user_operations()
    
    await message.answer(f"Рад познакомиться, {user.name}", reply_markup=menu)




async def main():
    from handlers import handlers
    from orderinng_handlers import ordering_handler
    from text_based_order_handler import text_based_handlers
    from middlewares import TextFormatter
    dp.message.outer_middleware(TextFormatter())
    dp.include_routers(handlers, ordering_handler, text_based_handlers)

    await dp.start_polling(bot)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(main())
    else:
        asyncio.run(main())
        
