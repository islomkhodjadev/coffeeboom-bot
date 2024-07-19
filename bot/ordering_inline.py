from aiogram.utils.keyboard import InlineKeyboardBuilder

from botAdmin.models import MenuCategory, MenuItem, TelegramUser, Orders

from aiogram.filters.callback_data import CallbackData
from asgiref.sync import sync_to_async
from django.db import transaction

class OrderMenuDataCalback(CallbackData, prefix="ordermenu"):
    id : int
    name: str


class OrderProductCallbackData(CallbackData, prefix="orderproduct"):
    id: int
    category: str



class OrderProduct(CallbackData, prefix="buy"):
    id: int
    

# this is for ordering the menu
async def order_menu_inline_buttons(order_id=None):
    
    
    @sync_to_async
    def hasorderItem(order_id):
        orders = Orders.objects.filter(id=order_id, complete=False)
        if orders.exists():
            order = orders.last()
            return order.orderitem.all().exists()
        
        else:
            return False
    
    menu = InlineKeyboardBuilder()
    all_objects = await sync_to_async(list, thread_sensitive=True)(MenuCategory.objects.all())


    for category in all_objects:
        menu.button(text=category.name, callback_data=OrderMenuDataCalback(id=category.pk, name=category.name))
        
    menu.adjust(3, 2)
    if order_id and await hasorderItem(order_id):
        
        menu.button(text="завершить заказ", callback_data=f"end:{str(order_id)}")
    
    return menu.as_markup()




async def product_buttons(id):
    products = InlineKeyboardBuilder()
    all_objects = await sync_to_async(list, thread_sensitive=True)(MenuItem.objects.filter(category=id))
    def get_cat(product):
        return product.category.name

    for product in all_objects:
        category = await sync_to_async(get_cat, thread_sensitive=True)(product=product)
        products.button(text=product.name, callback_data=OrderProductCallbackData(id=product.pk, category=category))
        
    products.adjust(3, 2)

    return products.as_markup()



async def buy_product_inline(id_product, user):
    button = InlineKeyboardBuilder()
    product = await sync_to_async(MenuItem.objects.get, thread_sensitive=True)(pk=id_product)
    
    button.button(text="купить", callback_data=OrderProduct(id=product.id))
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
    
    
        

async def  end_order_inline_button(order_id):
    button = InlineKeyboardBuilder()
    button.button(text=" end order", callback_data=str(order_id))
    return button.as_markup()





class OrderInfo(CallbackData, prefix="order_info"):
    order_id: int
    order_made_chat: int
    


async def get_order_inline(order_id: int, order_made_chat: int):
    button = InlineKeyboardBuilder()
    button.button(text="get order", callback_data=OrderInfo(order_id=order_id, order_made_chat=order_made_chat))
    
    return button.as_markup()


class OrderTaken(CallbackData, prefix="ready_order"):
    order_taken_by_id: int
    order_id: int




async def order_ready(order_taken_by_id, order_id):
    
    button = InlineKeyboardBuilder()
    button.button(text="order ready", callback_data=OrderTaken(order_taken_by_id=order_taken_by_id, order_id=order_id))
    
    return button.as_markup()

