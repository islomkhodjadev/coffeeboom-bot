from openai import OpenAI
import os
from dotenv import load_dotenv
from aiogram import types, Router, F
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext
from utils.gpt import get_ai_response
load_dotenv()


import os, django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from botAdmin.models import MenuItem, TelegramUser, Orders, MenuCategory




def formatt(user_message, extra_data=None):
    
    content = """

        Pay close attention that you can not send a word or a sentence that is not mentioned in the list, you should not be creative but a filter.
        You are being used as a middle layer, where you get message and identify key words and send only key words, you should try to understand what user said. It might be product, booking a place or ending a order or similar.
        User is likly to use Uzbek, Russian or English Language but he might also use different alphabets and he might also make grammatical errors pay attention to that, he might writte russian words with Latin or he might write Uzbek words with grammatical error but try to understand it.
        Below are given the format that you should convert from user text, and don't forget when you are sending a converted format don't send it with brackets it should be without any brackets.
        here are the formatting settings, these are menu settings: 
        >>  so if user asks about showing menu or similiar to thing: (меню)
        >> if someone asks about some category 
         If category names are mentined then don't make any otutput except following format product names.
        These are product names: """ \
         +  "\n".join([f"for {category.name} send - ({category.name}-{category.pk}-category)" for category in MenuCategory.objects.all()]) + """ 
         >> if user asks about ordering the food or similiar: (заказать блюда)
        >> if user asks about ordering the sit or similiar: (заказать места)
        >> if user asks something similiar to end order of food: (end)
        >> if user asks something cancel all product: (cancel all) 
        >> if user asks something similiar to cancel the order of the product: (cancel product)
        >> if user asks to cancel certian product where he mentions the product name then 
        If product names are mentined then don't make any otutput except following format product names.
        These are product names:
        """   \
          +  "\n".join([f"for {product.name} send - ({product.name}-{product.pk}-cancelproduct)" for product in MenuItem.objects.all()]) + """
        >> if user asks some product from the given list or summary is similiar to the product description product you should return the product like it is given  (product-<id>), 
        If the message user send means something like ordering x food and food in the following list then you send following format but if that is not in the list then just send what user wrote without any changes:
        If product names are mentined then don't make any otutput except following format product names.
        These are product names:
        
        """ + "\n".join([f"for {product.name} send - ({product.name}-{product.pk}-product)" for product in MenuItem.objects.all()])


    client = OpenAI(api_key=os.getenv("gpt_token"))
    
    
    if extra_data is not None:
        content += extra_data
        
    completion = client.chat.completions.create(
        
        model= "gpt-3.5-turbo",
        temperature=0.0,
	messages=[
            {"role": "system", "content": content},            {"role": "user", "content": user_message}
        ]
    )
    
    
    ai_response = completion.choices[0].message
    
    return ai_response.content.replace("(", "").replace(")", "")


text_based_handlers = Router(name="text based router")

from orderinng_handlers import order_sit_start, order_food, product_order, end_order, category_show
from handlers import menu_show
from aiogram.types.callback_query import CallbackQuery
from ordering_inline import order_menu_inline_buttons

handler_dict = {
    "заказать места": order_sit_start,
    "заказать блюда": order_food,
    "меню": menu_show,
    "product_order": product_order,
    
     
    
}



@text_based_handlers.message(F.text)
async def text_process(message: types.Message, state: FSMContext):
    text = await sync_to_async(formatt, thread_sensitive=True)(message.text)
    print(text)
    @sync_to_async
    def is_there_product(id):
        return MenuItem.objects.filter(id=id).exists()
    
    @sync_to_async
    def get_order(message: types.Message):
        user = TelegramUser.objects.get(id_user=message.from_user.id)
        order = Orders.objects.filter(user=user, complete=False).exists()
        if order:
            return Orders.objects.filter(user=user, complete=False).last()
        return False
    
    @sync_to_async
    def cancel_all_product(message: types.Message):
        user = TelegramUser.objects.get(id_user=message.from_user.id)
        order = Orders.objects.filter(user=user, complete=False).exists()
        
        if order:
            Orders.objects.get(user=user, complete=False).delete()
            
            return True
        
        return False
    
    @sync_to_async
    def cancel_last_product(message: types.Message, product_id=None):
        user = TelegramUser.objects.get(id_user=message.from_user.id)
        order = Orders.objects.filter(user=user).exists()
        
         
        if order:
            if Orders.objects.filter(user=user, complete=False).last().orderitem.all().exists():
                product = MenuItem.objects.get(pk=product_id)
                
                if (product_id is not None) and Orders.objects.filter(user=user, complete=False).last().orderitem.filter(product=product).exists():
                    print(product_id)
                    Orders.objects.filter(user=user, complete=False).last().orderitem.get(product=product).delete()
                else:
                    Orders.objects.filter(user=user, complete=False).last().orderitem.all().last().delete()
            
            return True
        
        return False
    
    if text in handler_dict:
        
        await handler_dict[text](message=message, state=state, data="")
        
    elif "product" == text.split("-")[-1] and await is_there_product(text.split("-")[1]):
        await handler_dict["product_order"](data={"menuItemId":text.split("-")[1]}, message=message)

    elif text.endswith("category"):
        await category_show(data={
            "menuId": text.split("-")[1],
            
        },
                            message=message)
        
    elif text == "end":
        
        order = await get_order(message)
        
        if order:
            await end_order(data={"order_id": order.pk}, message=message)
        else:
            await message.reply("пожалуйста, сначала закажите еды")
            
    elif text == "cancel product":
        await state.clear()
        await cancel_last_product(message)
        order = await get_order(message)
        all_buttons = await order_menu_inline_buttons(order.pk if order else None)
        await message.reply("сделано", reply_markup=all_buttons)
    elif text.endswith("cancelproduct"):
        print("cancelproduct worked")
        await state.clear()
        await cancel_last_product(message, text.split("-")[1])
        order = await get_order(message)
        all_buttons = await order_menu_inline_buttons(order.pk if order else None)
        await message.reply("сделано", reply_markup=all_buttons)
    elif text == "cancel all":
        
        order = await cancel_all_product(message)
        await message.reply("сделано ваш заказ отменено")
        
    else:
        
        # text = await sync_to_async(get_ai_response(), thread_sensitive=True)(message.text)
        await message.reply(text)
    
