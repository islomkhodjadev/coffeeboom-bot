from aiogram import BaseMiddleware
from aiogram.types import Message

from typing import Callable, Dict,  Any, Awaitable
from text_based_order_handler import formatt
from aiogram import types


class Heyyo:
    state = "hey"

class TextFormatter(BaseMiddleware):
    

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        data["hello"] = 12
        return await handler(event, data)
    
    # async def on_pre_process_message(self, message: types.Message, *args):
    #     print(message.text)
    #     message.text = "меню"
    #     return message
