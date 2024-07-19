from celery import shared_task
from datetime import datetime
from django.utils import timezone
from .views import send_image, send_media_group
import asyncio
from asgiref.sync import async_to_sync

from dotenv import load_dotenv
import os
load_dotenv()

TOKEN = os.getenv("tg_token")


@shared_task
def send_post(task_id):
    
    from .models import POSTCHANNEL
    
    instance = POSTCHANNEL.objects.get(id=task_id)
    urls = [image_instance.get_full_url for image_instance in instance.image.all()]
    
    send_media_group(urls, instance.caption, instance.chat.name)
    instance.delete()
    return urls

@shared_task
def delete_event(task_id):
    
    from .models import EventData
    
    
    EventData.objects.filter(pk=task_id).delete()
    
    
    
    return True










async def send_promotion_to_all(all_chat_id, image, caption):
    from aiogram.types.input_file import BufferedInputFile
    from aiogram.enums.parse_mode import ParseMode
    
    from aiogram import Bot
    
    bot = Bot(token=TOKEN)
    
    for chat_id in all_chat_id:
        print("working")
        await bot.send_photo(chat_id, photo=BufferedInputFile(image, filename="salom.jpeg"), parse_mode=ParseMode.HTML, caption=caption)
    





@shared_task
def send_promotion(task_id):
    
    from .models import TelegramUser,  Promotion 
    
    instance = Promotion.objects.get(pk=task_id)
    
    
    all_chat_id = [user.id_user for user in TelegramUser.objects.all()]
    asyncio.run(send_promotion_to_all(all_chat_id, instance.menu_item.image.read(), instance.caption))
    
    return True

