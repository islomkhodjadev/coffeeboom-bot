import os, django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()



import asyncio
from aiogram import  types, F, Router 
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import BufferedInputFile, FSInputFile
from aiogram.types.input_file import BufferedInputFile
from aiogram.enums.parse_mode import ParseMode

from botAdmin.models import TelegramUser, ChatMessage, MenuCategory, MenuItem

from asgiref.sync import sync_to_async

from texts import all_context, product_description, supported_html


from utils.yandex import yandex_stt_ru as yandex_stt
from utils.yandex import yandex_tts_ru as yandex_tts
from utils.gpt import get_ai_response

from utils.stt.stt_english import stt_english
from functions import extra_data_get, delayed_message
from inline_buttons import MenuDataCalback, menu_inline_buttons, product_buttons
from markups import menu as menu_products

handlers = Router()

from coffeeboom import bot




@handlers.message((F.voice | F.audio))
async def echo_audio(message: types.Message):
    from bot.coffeeboom import bot
    await message.bot.send_chat_action(chat_id=message.chat.id, action='upload_voice')
    file_id = message.voice.file_id if message.voice else message.audio.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    file_bytes = await bot.download_file(file_path)
    extra_data = await extra_data_get()
    text = yandex_stt(file_bytes.getvalue())
    main_content = await all_context(True)
    text = get_ai_response(text,
                           content=main_content,extra_data=extra_data )
    
    delayed_message(message)
    
    voice_file = BufferedInputFile(yandex_tts(text), "audio.ogg")
    await message.answer_voice(voice=voice_file)



@handlers.callback_query(F.data.startswith("menu"))
async def menu(query: CallbackQuery):
    menu_id = int(query.data.split(":")[1])
    
    instance = await sync_to_async(MenuCategory.objects.get, thread_sensitive=True)(
        id=menu_id
    )
    
    products = await product_buttons(instance.id)
    await query.message.delete()
    await query.message.answer_photo(photo=BufferedInputFile(instance.image.read(), filename=instance.name+".jpeg"), caption=instance.name, reply_markup=products)
    

# product handler
@handlers.callback_query(F.data.startswith("product"))
async def menu(query: CallbackQuery):
    product_id = int(query.data.split(":")[1])
    
    
    instance = await sync_to_async(MenuItem.objects.get, thread_sensitive=True)(
        id=product_id
    )
    
    
    await query.message.delete()
    await query.message.answer_photo(photo=BufferedInputFile(instance.image.read(), filename=instance.name+".jpeg"), caption=product_description(instance.name, instance.price, instance.description), parse_mode=ParseMode.HTML, reply_markup=menu_products)







# see menu handler
@handlers.message(F.text=="меню")
async def menu_show(message: types.Message, **kwargs):
    await message.delete()
    all_data = await menu_inline_buttons()
    
    await message.answer(text="меню:", reply_markup=all_data)

