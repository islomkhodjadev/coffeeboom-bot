import os, django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from botAdmin.models import TelegramUser, ChatMessage, MenuCategory, MenuItem, Orders, OrderItem, TableNumber

from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext
from aiogram.filters import Filter
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery


from utils.gpt import get_ai_response


class helloFilter(Filter):
    def __init__(self, data: str) -> None:
        print(data.__dict__)
        
    async def __call__(self, message: Message) -> bool:
        
        return True
    


class ChatType(Filter):
    def __init__(self, chat_type: str) -> None:
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        return message.chat.type == self.chat_type
    
class OwnerOnly(Filter):
    def __init__(self, owner: str) -> None:
        self.owner_id = owner

    async def __call__(self, query: CallbackQuery) -> bool:
        return query.from_user.id == self.owner_id and query.data.startswith("ready_order")
    
class TableChoose(Filter):
    

    async def __call__(self, message: Message) -> bool:
        text = get_ai_response(message.text, "you should summarize and return the number which user asked only number, if in user response there is no number then return nothing empty")
            
        
        
        @sync_to_async
        def has_table():
            
            return TableNumber.objects.filter(number=text).exists()
        return text.isdigit() and await has_table()

class IsDigit(Filter):

        def __init__(self, state):
            self.state = state
            
    
        async def __call__(self, message: Message, state: FSMContext) -> bool:
            
            text = get_ai_response(message.text, "you must understand which number user sent and return it to me as number without aanything")
            
            return text.isdigit() and await state.get_state() == self.state
        