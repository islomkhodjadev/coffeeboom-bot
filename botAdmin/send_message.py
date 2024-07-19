from telegram import Bot, InputMediaPhoto
from telegram.error import TelegramError

def send_image(image_urls: list[str], caption: str):
    print("Sending images to channel...")
    bot = Bot(token='')
    channel_id = '@Ringaiofficial'

    # Prepare media group
    media = [InputMediaPhoto(media=url, caption=caption if i == 0 else None) for i, url in enumerate(image_urls)]

    try:
        # Sending media group synchronously
        bot.send_media_group(chat_id=channel_id, media=media)
        print("Images successfully sent.")
    except TelegramError as e:
        print(f"Failed to send images: {e}")


urls = ["https://images.uzum.uz/cn6ss1ps99ouqbfui9e0/original.jpg", "https://images.uzum.uz/cn6ss1ps99ouqbfui9e0/original.jpg"]
send_image(urls, "salom")
