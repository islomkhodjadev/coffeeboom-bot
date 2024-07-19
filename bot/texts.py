



import os, django
from asgiref.sync import sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from botAdmin.models import MenuItem, Orders





def product_description(product_name, product_price, product_description):
    return f"<b>{product_name}</b>\n" \
        f"<b>цена: </b><i>{product_price} сум</i>\n" \
            f"<blockquote expandable>{product_description}</blockquote>"


async def get_all_promotion_products():
    all_objects = await sync_to_async(list, thread_sensitive=True)(MenuItem.objects.filter(advertise=True))
    if all_objects:
        text = """вот список блюд, которые вы должны продвигать, используя самые современные маркетинговые навыки, всегда старайтесь
         продавать и побуждать людей покупать их, всегда в каждом ответе старайтесь продать их,
          вы должны включать это в каждый ответ, даже если это не связано::  """
        for product in all_objects:
            text += product_description(product.name, product.price, product.description)

        return text
    return ""


supported_html = """try to write always including emojies you must use emojies a lot, when you are writing something and want to use formatting only use these formatting settings dont use **, or other signs only these ones here are :
<b>bold</b>, <strong>bold</strong>
<i>italic</i>, <em>italic</em>
<u>underline</u>, <ins>underline</ins>
<s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
<span class="tg-spoiler">spoiler</span>, <tg-spoiler>spoiler</tg-spoiler>
<b>bold <i>italic bold <s>italic bold strikethrough <span class="tg-spoiler">italic bold strikethrough spoiler</span></s> <u>underline italic bold</u></i> bold</b>
<a href="http://www.example.com/">inline URL</a>
<a href="tg://user?id=123456789">inline mention of a user</a>
<tg-emoji emoji-id="5368324170671202286">👍</tg-emoji>
<code>inline fixed-width code</code>
<pre>pre-formatted fixed-width code block</pre>
<pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>
<blockquote>Block quotation started\nBlock quotation continued\nThe last line of the block quotation</blockquote>
<blockquote expandable>Expandable block quotation started\nExpandable block quotation continued\nExpandable block quotation continued\nHidden by default part of the block quotation started\nExpandable block quotation continued\nThe last line of the block quotation</blockquote>"""







main_content = """
you are the online marketing agent of Cofeeboom, you must make eveyrthing to promote 
and encourage people to come to 
Cofeeboom, be polite very polite,  Cofeeboom (sometimes spelled "Coffee Boom") 
is a prominent coffee shop chain with locations in both Tashkent, 
Uzbekistan, and various cities across Kazakhstan, including Astana and Almaty. 
These cafes are known for their lively, modern vibe and a broad menu that caters to a variety of tastes, 
from traditional coffee and specialty drinks to Western-style fast food and local dishes.

In Tashkent, Coffee Boom is situated inside the "Poytaht" Business Center,
offering a convenient spot for both takeaway and delivery services.
They are recognized for their use of 100% Arabica beans, 
signature Boom Ice Tea, and a selection of frappuccinos,
with a portion of their sales going to charity.

In Kazakhstan, the Coffee Boom outlets are typically found in city centers and shopping malls, 
making them accessible spots for both residents and visitors.
The chain stands out for its early opening hours, which is somewhat unusual in the region,
and offers an extensive menu that includes not only beverages but also breakfast options,
burgers, sandwiches, and vegetarian meals
. The atmosphere in these cafes is generally described as friendly and cozy, 
often bustling with activity.

contacts :
+998991151999
+998993102999
:
web site: www.coffeeboom.kz ;
instagram: https://www.instagram.com/coffeeboom.tashkent/ ;


"""


async def all_context(is_voice=False):
    if is_voice:
        return "you must speak in russian always you must speak in uzbek remember \n" + main_content + await get_all_promotion_products()
    return main_content + await get_all_promotion_products() + supported_html





async def order_products_list(order_id):
    @sync_to_async(thread_sensitive=True)
    def get_or_order_text():
        order = Orders.objects.get(
            pk=order_id,
            complete=False
        )
        
        products = order.orderitem.all()
        text = (f"<b>Номер места: {order.table.number} </b>" + 
            f"<b>пользователь:</b> {order.user.username} заказал: \n"
            + "\n".join(
                [
                    f"<b>Название продукта:</b> {order_item.product.name} \n"
                    f"<b>количество:</b> {order_item.count} \n"
                    f"<b>цена:</b> {order_item.count * order_item.product.price} \n"
                    for order_item in products
                ]
            )
            + f"\n<b>Общая цена:</b> {order.total_price}"
        )


        return text
    
    return await get_or_order_text()

