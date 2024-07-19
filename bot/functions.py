
import os, django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from aiogram.enums.parse_mode import ParseMode
from asgiref.sync import sync_to_async
from botAdmin.models import EventData


async def extra_data_get():
    # Using Django models after proper setup
    objects = await sync_to_async(list, thread_sensitive=True)(EventData.objects.all())
    if objects:
        content = "here extra data that you should know it is about new events when someone asks here is info " + \
                  " \n ".join([obj.content for obj in objects])
    else:
        content = ""

    return content


import asyncio
from coffeeboom import bot
from aiogram import types

from utils.gpt import get_ai_response

last_message_time = {}
from texts import get_all_promotion_products, supported_html
async def send_delayed_message(chat_id, promote=False):
    
    await asyncio.sleep(10)
    await bot.send_chat_action(chat_id=chat_id, action='typing')
    if (asyncio.get_event_loop().time() - last_message_time.get(chat_id, 0)) >= 10 and not promote:
        await bot.send_message(chat_id,  "есть у вас какие то еще вопросы?")
        last_message_time[chat_id] = asyncio.get_event_loop().time()
        asyncio.create_task(send_delayed_message(chat_id=chat_id, promote=True))

    elif promote and (asyncio.get_event_loop().time() - last_message_time.get(chat_id, 0)) >= 10:
        text = await get_all_promotion_products()
        
        text = get_ai_response("write some beautifull promotion and give it in russian", content=text + supported_html)

        await bot.send_message(chat_id,  text, parse_mode=ParseMode.HTML)
        
        
def delayed_message(message: types.Message):
    
    last_message_time[message.chat.id] = asyncio.get_event_loop().time()
    asyncio.create_task(send_delayed_message(message.chat.id))
