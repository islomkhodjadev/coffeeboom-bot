import os, django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()


from aiogram.types.input_file import FSInputFile
from utils.gpt import get_ai_response
import asyncio
from aiogram import  types, F, Router 
from aiogram.types.callback_query import CallbackQuery

from aiogram.types.input_file import BufferedInputFile
from aiogram.types import URLInputFile

from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from botAdmin.models import TelegramUser, OrderTableItem, MenuCategory, MenuItem, Orders, OrderItem, TableNumber

from filters import OwnerOnly, TableChoose, IsDigit

from asgiref.sync import sync_to_async

from texts import all_context, product_description, supported_html, order_products_list


from ordering_inline import OrderMenuDataCalback, order_menu_inline_buttons, product_buttons, buy_product_inline, end_order_inline_button, get_order_inline, order_ready
from markups import menu as menuButton
ordering_handler = Router()

from coffeeboom import bot



class CountOfProduct(StatesGroup):
    count = State()
    prouct_id = State()
    order_id = State()


class SitFirst(StatesGroup):
    sitPlace = State()
    
    
class OrderSit(StatesGroup):
    sitNumber = State()
    date = State()
    
    
@ordering_handler.message(F.text == "заказать места")
async def order_sit_start(message: types.Message, state: FSMContext, **kwargs):
    await state.set_state(OrderSit.sitNumber)
    
    await message.answer_photo(URLInputFile("https://media-cdn.tripadvisor.com/media/photo-s/10/ce/ff/48/20170927-143014-largejpg.jpg"), caption="пожалуйста, выберите номер места и напишите его")
    await message.delete()


@ordering_handler.message(OrderSit.sitNumber)
async def order_sit(message: types.Message, state: FSMContext, **kwargs):
    
    @sync_to_async
    def sitSet():
        sit_number = get_ai_response(message.text, "you must understand which number user sent and return it to me as number without aanything")
        print(sit_number)
        
        if sit_number.isdigit() and TableNumber.objects.filter(number=sit_number).exists():
            order = OrderTableItem.objects.create(
                user=TelegramUser.objects.get(id_user=message.from_user.id),
                table=TableNumber.objects.get(number=sit_number)
            )
            return order
        return False
    
    result = await  sitSet()
    if not result:
        await message.answer("пожалуйста, укажите правильное место")
    else:
        await state.set_state(OrderSit.date)
        await message.answer("пожалуйста, укажите дату и время, когда вы хотите сделать заказ, например, 17 января в 12:00")


@ordering_handler.message(OrderSit.date)
async def order_sit(message: types.Message, state: FSMContext, **kwargs):
    await state.clear()
    
    @sync_to_async
    def sitSet():
        
        
        
        order = OrderTableItem.objects.filter(
                user=TelegramUser.objects.get(id_user=message.from_user.id)).last()
        order.date = message.text
        order.save()
        
        return order, order.user, order.table
        
    result = await sitSet()
    await bot.send_message("-1002179328076", f"{result[1].name}: {result[1].phone_number} \n {result[0].date} на \n {result[2].number}-е место заказано")
    await message.answer("Спасибо за заказ места", reply_markup=menuButton)






@ordering_handler.message(F.text=="заказать блюда")
async def order_food(message: types.Message, state: FSMContext, **kwargs):
    await state.set_state(SitFirst.sitPlace)
    
    
    await message.answer_photo(URLInputFile("https://media-cdn.tripadvisor.com/media/photo-s/10/ce/ff/48/20170927-143014-largejpg.jpg"), caption="пожалуйста, выберите номер места и напишите его")
    await message.delete()



# see menu hanlder
@ordering_handler.callback_query(F.data.startswith("ordermenu"))
async def category_show(query: CallbackQuery=None, **kwargs):
    
    
    
    
    if not ("data" in kwargs):
        menu_id = int(query.data.split(":")[1])
        
        instance = await sync_to_async(MenuCategory.objects.get, thread_sensitive=True)(
            id=menu_id
        )
        
        products = await product_buttons(instance.id)
        await query.message.delete()
        await query.message.answer_photo(photo=BufferedInputFile(instance.image.read(), filename=instance.name+".jpeg"), caption=instance.name, reply_markup=products)
    else:
        menu_id = int(kwargs["data"]["menuId"])
        message = kwargs["message"]
        instance = await sync_to_async(MenuCategory.objects.get, thread_sensitive=True)(
            id=menu_id
        )
        
        products = await product_buttons(instance.id)
        
        await message.answer_photo(photo=BufferedInputFile(instance.image.read(), filename=instance.name+".jpeg"), caption=instance.name, reply_markup=products)
    



# product handler
@ordering_handler.callback_query(F.data.startswith("orderproduct"))
async def product_order(query: CallbackQuery=None, **kwargs):
    if not ("data" in kwargs):
        product_id = int(query.data.split(":")[1])
        
        instance = await sync_to_async(MenuItem.objects.get, thread_sensitive=True)(
            id=product_id
        )
        
        
        await query.message.delete()
        button = await buy_product_inline(product_id, query.message.from_user)
        
        await query.message.answer_photo(photo=BufferedInputFile(instance.image.read(), filename=instance.name+".jpeg"), caption=product_description(instance.name, instance.price, instance.description), parse_mode=ParseMode.HTML, reply_markup=button)
    else:
        menu_id = int(kwargs["data"]["menuItemId"])
        message = kwargs["message"]
        instance = await sync_to_async(MenuItem.objects.get, thread_sensitive=True)(
            id=menu_id
        )
        
        
        
        button = await buy_product_inline(instance.id, message.from_user)
        
        await message.answer_photo(photo=BufferedInputFile(instance.image.read(), filename=instance.name+".jpeg"), caption=instance.name, reply_markup=button)
    

from django.db import transaction

@ordering_handler.callback_query(F.data.startswith("buy"))
async def ordering_product(query: CallbackQuery=None, state: FSMContext=None, **kwargs):
    
        
    product = await sync_to_async(MenuItem.objects.get, thread_sensitive=True)(pk=query.data.split(":")[1])
    user_object = await sync_to_async(TelegramUser.objects.get, thread_sensitive=True)(id_user=query.from_user.id)

    
    
    @sync_to_async(thread_sensitive=True)
    @transaction.atomic
    def get_or_create_order():
        order, created_at = Orders.objects.get_or_create(
            user=user_object,
            complete=False
        )
        
        
        if order.table:
            
            OrderItem.add_product(order, product)
        
            return order, True
        
        return order, False
        
        
    
    

    order, flag = await get_or_create_order()
    
    
    if order and flag:
        await state.set_state(CountOfProduct.count)
        
        await state.update_data(product_id = product.pk, order_id=order.pk)
            
            
        await query.answer()
        await query.message.delete()
        await query.message.answer("пожалуйста, введите количество этого товара цифрами")
    else:
            
            
            
        await state.set_state(SitFirst.sitPlace)
        await state.update_data(product_id = f"{product.pk}" )
        await query.message.answer_photo(URLInputFile("https://www.barniescoffee.com/cdn/shop/articles/bar-1869656_1920.jpg?v=1660683986"), caption="сначала выберите стол, за которым вы сидите, затем еще раз спросите об этом продукте")
        await query.message.delete()
            
    

@ordering_handler.message(IsDigit(CountOfProduct.count))
async def order(message: types.Message, state: FSMContext, **kwargs):
    text = get_ai_response(message.text, "you must understand which number user sent and return it to me as number without aanything")
          
    await state.update_data(count=text)
    data = await state.get_data()
    await state.clear()
    
    
    product = await sync_to_async(MenuItem.objects.get, thread_sensitive=True)(pk=data["product_id"])
    
    
    @sync_to_async(thread_sensitive=True)
    @transaction.atomic
    def get_or_create_order():
        order = Orders.objects.get(
            pk=data["order_id"],
            complete=False
        )
        
        OrderItem.add_product(order, product, text)

        return order

    order = await get_or_create_order()

    
    all_data = await order_menu_inline_buttons(order_id=order.pk)
    
    await message.answer(text="Что-нибудь еще вам нужно?", reply_markup=all_data)





@ordering_handler.message(SitFirst.sitPlace)
@ordering_handler.message(TableChoose())
async def menu_start(message: types.Message, state: FSMContext, **kwargs):
    sitPlace = get_ai_response(message.text, "you must understand which number user sent and return it to me as number without aanything")
    data = await state.get_data()
    await state.clear()
    
    @sync_to_async
    def create_table_and_order(table_sit_number: int):
        if TableNumber.objects.filter(number=table_sit_number).exists():
            
            table_sit = TableNumber.objects.get(number=table_sit_number)
            
            order = Orders.objects.filter(
                user=TelegramUser.objects.get(id_user=message.from_user.id),
                complete=False,
                # table = table_sit
                )
            
            if order.exists():
                order = Orders.objects.get(
                user=TelegramUser.objects.get(id_user=message.from_user.id),
                complete=False,
                
                )
                order.table = table_sit
                order.save()
                return order, False 
            
            order = Orders.objects.create(
                user=TelegramUser.objects.get(id_user=message.from_user.id),
                complete=False,
                table = table_sit
                )
            
            return order
        else:
            return False
        
        
        
    
    order = await create_table_and_order(sitPlace)
    if not order :
        await state.clear()
        await state.set_state(SitFirst.sitPlace)
        
        await message.answer("пожалуйста, укажите правильное место")
        
    elif (not isinstance(order, tuple) and order) or ("produc_id" not in data):
        await message.delete()
        all_data = await order_menu_inline_buttons()
        await message.answer(text="Теперь вы можете начать заказ", reply_markup=all_data)
    else:
        
        instance = await sync_to_async(MenuItem.objects.get, thread_sensitive=True)(
            id=data["product_id"]
        )
        
        
        
        button = await buy_product_inline(instance.id, message.from_user)
        
        await message.answer_photo(photo=BufferedInputFile(instance.image.read(), filename=instance.name+".jpeg"), caption=instance.name, reply_markup=button)
    

# product handler
@ordering_handler.callback_query(F.data.startswith("end"))
async def end_order(query: CallbackQuery=None, **kwargs):
    
    
    
    
    if not ("data" in kwargs):
        order_id = int(query.data.split(":")[1])
        
        order = await sync_to_async(Orders.objects.get, thread_sensitive=True)(
                pk=order_id,
                complete=False
            )
        
        buttons = await get_order_inline(int(order_id), int(query.from_user.id))
        text = await order_products_list(order_id)
        await query.message.edit_text(text, parse_mode=ParseMode.HTML)
        await bot.send_message("-1002179328076", text, reply_markup=buttons, parse_mode=ParseMode.HTML)
    else:
        
        order_id = int(kwargs["data"]["order_id"])
        
        order = await sync_to_async(Orders.objects.get, thread_sensitive=True)(
                pk=order_id,
                complete=False
            )
        message = kwargs["message"]
        
        buttons = await get_order_inline(int(order_id), int(message.from_user.id))
        text = await order_products_list(order_id)
        await message.message.edit_text(text, parse_mode=ParseMode.HTML)
        await bot.send_message("-1002179328076", text, reply_markup=buttons, parse_mode=ParseMode.HTML)



@ordering_handler.callback_query(F.data.startswith("order_info"))
async def get_order(query: CallbackQuery, **kwargs):
    data = query.data.split(":")
    
    @sync_to_async(thread_sensitive=True)
    @transaction.atomic
    def get_order():
        order = Orders.objects.get(
            pk=data[1],
            complete=False
        )

        return order, order.user.username
    
    order, username = await get_order()
    button = await order_ready(query.from_user.id, order.id)
    await bot.send_message(data[2], f"{query.from_user.username} получит ваш заказ \n скоро он будет доставлен вам", parse_mode=ParseMode.HTML)
    await query.message.edit_text(query.message.text, reply_markup=button, parse_mode=ParseMode.HTML)



@ordering_handler.callback_query(OwnerOnly(F.from_user.id))
async def ready_order(query: CallbackQuery, **kwargs):
    
    data = query.data.split(":")
    
    @sync_to_async(thread_sensitive=True)
    @transaction.atomic
    def get_and_complete():
        order = Orders.objects.get(
            pk=data[2],
            complete=False
        )
        order.complete = True
        order.save()
        
        return order, order.user.id_user
    
    order, order_owner_id = await get_and_complete()
    
    
    await query.answer()
    await query.message.edit_text(f"заказ по id: {order.pk}, \nвыполнен пользователем {query.from_user.username}\n детали заказа: \n {query.message.text}", parse_mode=ParseMode.HTML)
    await bot.send_message(order_owner_id, f"ваш заказ готов, скоро вы получите его")
