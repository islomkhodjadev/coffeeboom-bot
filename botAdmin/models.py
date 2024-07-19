from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .tasks import send_post, delete_event, send_promotion
from celery import current_app
from dotenv import load_dotenv
import os
load_dotenv()


class TelegramUser(models.Model):
    id_user = models.TextField(verbose_name=_("User ID"), unique=True)
    username = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Username"))
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, verbose_name=_("Profile Picture"))
    bio = models.TextField(null=True, blank=True, verbose_name=_("Bio"))
    phone_number = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Phone Number"))
    name = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Name"))
    surname = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Surname"))
    
    class Meta:
        verbose_name = _("Telegram User")
        verbose_name_plural = _("Telegram Users")

    def __str__(self):
        return self.username or _("Unknown User")
    

class ChatMessage(models.Model):
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, verbose_name=_("Telegram User"))
    text = models.TextField(verbose_name=_("Text"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"))
    is_admin = models.BooleanField(default=False, verbose_name=_("Is Admin"))

    class Meta:
        verbose_name = _("Chat Message")
        verbose_name_plural = _("Chat Messages")

    def __str__(self):
        return f"{self.telegram_user.username}: {self.text}"

class Image(models.Model):
    image = models.ImageField(upload_to="posts/", verbose_name=_("Image"))
    post = models.ForeignKey("POSTCHANNEL", related_name="image", on_delete=models.CASCADE, verbose_name=_("Post"))

    @property
    def get_full_url(self):
        from django.conf import settings
        return f"{settings.SITE_URL}{self.image.url}"

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")

class Chats(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Chat Name"))

    class Meta:
        verbose_name = _("Chat")
        verbose_name_plural = _("Chats")
    def __str__(self):
        return self.name

class POSTCHANNEL(models.Model):
    caption = models.TextField(verbose_name=_("Caption"))
    task_time = models.DateTimeField(verbose_name=_("Task Time"))
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE, verbose_name=_("Chat"))
    ai_caption = models.BooleanField(default=False, verbose_name=_("AI Generated Caption"))

    def save(self, *args, **kwargs):
        if self.ai_caption:
            import os
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("gpt_token"))

            completion = client.chat.completions.create(
                model="gpt-4-turbo",
                temperature=0.4,
                messages=[
                    {"role": "system", "content": "You should rewrite this caption to include emojis and hashtags, write the caption in the specified language."},
                    {"role": "user", "content": self.caption}
                ]
            )

            ai_response = completion.choices[0].message
            self.caption = ai_response.content

        super().save(*args, **kwargs)
        
        if self.task_time > timezone.now():
            eta = self.task_time
            send_post.apply_async((self.id,), eta=eta)

    class Meta:
        verbose_name = _("Post Channel")
        verbose_name_plural = _("Post Channels")

class EventData(models.Model):
    expire_date = models.DateTimeField(verbose_name=_("Expire Date"))
    content = models.TextField(verbose_name=_("Content"))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        eta = self.expire_date
        delete_event.apply_async((self.id,), eta=eta)

    class Meta:
        verbose_name = _("Event Data")
        verbose_name_plural = _("Event Data")
    

class MenuCategory(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Category Name"))
    image = models.ImageField(upload_to="menu/category/", verbose_name=_("Image"))

    class Meta:
        verbose_name = _("Menu Category")
        verbose_name_plural = _("Menu Categories")

    def __str__(self):
        return self.name
    
    
class MenuItem(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Item Name"))
    image = models.ImageField(upload_to="menu/menu-items/", verbose_name=_("Image"))
    price = models.IntegerField(verbose_name=_("Price"))
    description = models.TextField(verbose_name=_("Description"))
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name="item", verbose_name=_("Category"))
    advertise = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Menu Item")
        verbose_name_plural = _("Menu Items")

    def __str__(self):
        return self.name



class Promotion(models.Model):
    caption = models.TextField(verbose_name=_("Caption"))
    period = models.PositiveIntegerField()
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE, verbose_name=_("Chat"))
    ai_caption = models.BooleanField(default=False, verbose_name=_("AI Generated Caption"))
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="promotion")
    
    
    def save(self, *args, **kwargs):
        from datetime import datetime, timedelta
        if self.ai_caption:
            from openai import OpenAI
            
            from bot.texts import supported_html, product_description
            
            client = OpenAI(api_key=os.getenv("gpt_token"))

            completion = client.chat.completions.create(
                model="gpt-4-turbo",
                temperature=0.4,
                messages=[
                    {"role": "system", "content": """You should rewrite this caption to include emojis and hashtags,
                     write the caption in the specified language. 
                     promote given product make it for promotion only write the end user message dont include your own
                     things only direct promotion using the marketing skill here is the product: """ +product_description(product_description=self.menu_item.description, product_price=self.menu_item.price, product_name=self.menu_item.name)  + supported_html},
                    {"role": "user", "content": self.caption}
                ]
            )

            ai_response = completion.choices[0].message
            self.caption = ai_response.content

        super().save(*args, **kwargs)
        eta = datetime.now() + timedelta(seconds=self.period)
        if eta > datetime.now():
            
            
            send_promotion.apply_async((self.id,))

    class Meta:
        verbose_name = _("Promotion")
        verbose_name_plural = _("Promotion")



class TableNumber(models.Model):
    number = models.PositiveIntegerField()



class Orders(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="orders")
    created_time = models.DateTimeField(auto_now_add=True)
    table = models.ForeignKey(TableNumber, on_delete=models.CASCADE, related_name="orders", null=True, blank=True)
    complete = models.BooleanField(default=False)

    @property
    def total_price(self):
        return sum(order_item.count * order_item.product.price for order_item in self.orderitem.all())
    
    
from django.db import transaction


class OrderItem(models.Model):
    product = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="orderitem")
    count = models.PositiveBigIntegerField(null=True, blank=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name="orderitem")
    
    @classmethod
    def add_product(cls, order, product, count=None):
        with transaction.atomic():
            order_item, created = cls.objects.get_or_create(
                order=order,
                product=product,
                defaults={'count': count}  # if count is None, default to 1
            )
            
            if not created and count is not None:
                order_item.count = int(count)
                order_item.save()
            return order_item


class OrderTableItem(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="ordertableitem")
    table = models.ForeignKey(TableNumber, on_delete=models.CASCADE, related_name="ordertableitem")
    time = models.CharField(max_length=200)

