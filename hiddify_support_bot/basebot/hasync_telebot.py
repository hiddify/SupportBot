from typing import Callable
from telebot.async_telebot import AsyncTeleBot,logger
from collections import defaultdict
class HAsyncTeleBot(AsyncTeleBot):
    async def get_user_data(self,user_id,chat_id=None):
        try:
            async with self.retrieve_data(user_id,chat_id) as data:
                return data
        except:
            return {}
    async def add_user_data(self,user_id,chat_id=None,**kwargs):
        try:
            await self.add_data(user_id,chat_id,**kwargs)
        except:
            await self.set_state(user_id,"-",chat_id)
            await self.add_data(user_id,chat_id,**kwargs)
        
    def step_handler(self):
        """
            This decorator should be on top of a method for being used as step handeler

            Example: 
            @bot.step_handler()
            def test(message):
                pass
        """
        def decorator(handler):
            handler_name = handler.__name__
            module_name = handler.__module__
            signature = f"{hash(handler.__code__.co_filename)}:{module_name}.{handler_name}:{handler.__code__.co_firstlineno}"
            async def wrapper(*args, **kwargs):
                msg=args[0]
                async with self.retrieve_data(msg.from_user.id,msg.chat.id) as data:
                    step_kwargs=data.get('__step_handler_kwargs__',{})
                    step_args=data.get('__step_handler_args__',())
                    if '__step_handler_kwargs__' in data:
                        del data['__step_handler_kwargs__']
                    if '__step_handler_args__' in data:
                        del data['__step_handler_args__']
                    if '__step__' in data:
                        del data['__step__']
                return await handler(*args, *step_args, **kwargs, **step_kwargs)
            self.message_handlers.insert(0,{
                'function': wrapper,
                'pass_bot': False,
                'filters': {'step': signature}
            })
            wrapper.signature = signature
            return wrapper
        return decorator
    
    async def register_next_step_handler(self, user_id: int, chat_id: int, callback: Callable, *args, **kwargs) -> None:
        """
        Registers a callback function to be notified when new message arrives after `message`.

        Warning: In case `callback` as lambda function, saving next step handlers will not work.

        :param message: The message for which we want to handle new message in the same chat.
        :type message: :class:`telebot.types.Message`

        :param callback: The callback function which next new message arrives.
        :type callback: :obj:`Callable[[telebot.types.Message], None]`

        :param args: Args to pass in callback func

        :param kwargs: Args to pass in callback func

        :return: None
        """

        if not hasattr(callback,'signature'):
            raise ValueError("Do not forget to add @bot.step_handler() before function")
        
        await self.add_user_data(user_id, chat_id, __step__=callback.signature, __step_handler_args__=args, __step_handler_kwargs__=kwargs )


    def callback_query_handler(self, func=None,**kwargs):
        if func is None: func=lambda call:True
        return super().callback_query_handler(func,**kwargs)

