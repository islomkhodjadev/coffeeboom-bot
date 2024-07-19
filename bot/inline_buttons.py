from aiogram.utils.keyboard import InlineKeyboardBuilder

from botAdmin.models import MenuCategory, MenuItem, TelegramUser, Orders

from aiogram.filters.callback_data import CallbackData
from asgiref.sync import sync_to_async
from django.db import transaction

class MenuDataCalback(CallbackData, prefix="menu"):
    id : int
    name: str


class ProductCallbackData(CallbackData, prefix="product"):
    id: int
    category: str



class OrderProduct(CallbackData, prefix="buy"):
    id: int
    


async def menu_inline_buttons():
    menu = InlineKeyboardBuilder()
    all_objects = await sync_to_async(list, thread_sensitive=True)(MenuCategory.objects.all())


    for category in all_objects:
        menu.button(text=category.name, callback_data=MenuDataCalback(id=category.pk, name=category.name))
        
    menu.adjust(3, 2)

    return menu.as_markup()


async def menu_inline_buttons():
    menu = InlineKeyboardBuilder()
    all_objects = await sync_to_async(list, thread_sensitive=True)(MenuCategory.objects.all())


    for category in all_objects:
        menu.button(text=category.name, callback_data=MenuDataCalback(id=category.pk, name=category.name))
        
    menu.adjust(3, 2)

    return menu.as_markup()



async def product_buttons(id):
    products = InlineKeyboardBuilder()
    all_objects = await sync_to_async(list, thread_sensitive=True)(MenuItem.objects.filter(category=id))
    def get_cat(product):
        return product.category.name

    for product in all_objects:
        category = await sync_to_async(get_cat, thread_sensitive=True)(product=product)
        products.button(text=product.name, callback_data=ProductCallbackData(id=product.pk, category=category))
        
    products.adjust(3, 2)

    return products.as_markup()



async def buy_product_inline(id_product, user):
    button = InlineKeyboardBuilder()
    product = await sync_to_async(MenuItem.objects.get, thread_sensitive=True)(pk=id_product)
    
    button.button(text="купить", callback_data=OrderProduct(product.id))
    return button.as_markup()



async def buy_it(id_product, user):
    
    product = await sync_to_async(MenuItem.objects.get, thread_sensitive=True)(pk=id_product)
    user_object = await sync_to_async(TelegramUser.objects.get, thread_sensitive=True)(id_user=user.id)
    
    @sync_to_async(thread_sensitive=True)
    @transaction.atomic
    def get_or_create_order():
        order, created = Orders.objects.get_or_create(
            user=user_object,
            complete=False
        )
        order.products.add(product)
        return order
    
    order = await get_or_create_order()
    
    
        
    
    
    
    
