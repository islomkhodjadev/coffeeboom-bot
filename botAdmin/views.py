# from django.shortcuts import render

from aiogram import Bot, types
import asyncio

from dotenv import load_dotenv
import os
load_dotenv()

TOKEN = os.getenv("tg_token")

async def send_image(image_urls: list[str], caption: str, chat: str):
    print("salom send image")
    bot = Bot(token=TOKEN)

    channel_id = chat

    media = [types.InputMediaPhoto(media=url, caption = caption if i ==0 else None ) for i, url in enumerate(image_urls)]
    bot.send_media_group(chat_id=channel_id, media=media)

    await bot.session.close()
    return "Sucessfull"



import requests
import json

def send_media_group(media_urls, caption, chat: str):
    bot_token = TOKEN
    chat_id = chat
    url = f"https://api.telegram.org/bot{bot_token}/sendMediaGroup"
    
    
    media_files = []
    for i, media_url in enumerate(media_urls):
        response = requests.get(media_url)
        if response.status_code == 200:
            file_key = f"photo{i}"
            media_files.append((file_key, ('file.jpg', response.content, 'image/jpeg')))
        else:

            return f"Failed to download media from {media_url}"
    
    # Prepare the media payload
    media = [{"type": "photo", "media": f"attach://photo{i}", "caption": caption if i == 0 else ""} for i in range(len(media_files))]
    
    payload = {
        "chat_id": chat_id,
        "media": json.dumps(media)  # Ensure media payload is JSON encoded
    }
    
    # Include the media files in the request
    response = requests.post(url, data=payload, files=media_files)
    
    if response.status_code == 200:
        return "Successful"
    else:

        return f"Failed: {response.status_code} {response.text}"




