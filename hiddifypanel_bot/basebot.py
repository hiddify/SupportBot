#!/usr/bin/python

import telebot
import uuid
import logging
from .hiddifyapi.api import HiddifyApi
from telebot import TeleBot, ExceptionHandler, custom_filters,types
from telebot.storage import StateMemoryStorage
from telebot.types import Message
from telebot import handler_backends
import os
from dotenv import load_dotenv
from enum import Enum

load_dotenv()
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)  # Outputs debug messages to console.

HIDDIFYPANEL_USER_LINK = os.getenv("HIDDIFYPANEL_USER_LINK")
HIDDIFYPANEL_ADMIN_LINK = os.getenv("HIDDIFYPANEL_ADMIN_LINK")
BOT_TOKEN = os.getenv("BOT_TOKEN")

state_storage = StateMemoryStorage()  # you can init here another storage



class Role(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    AGENT = "agent"
    USER = "user"
    UNKNOWN="unknown"


class MyExceptionHandler(ExceptionHandler):
    def handle(self, exception):
        logger.error(exception)


bot: TeleBot = TeleBot(
    BOT_TOKEN,
    exception_handler=MyExceptionHandler(),
    use_class_middlewares=True,
    state_storage=state_storage,
)

bot.remove_webhook()


class DataStorage:
    def __init__(self, user_id, chat_id):
        self.user_id = user_id
        self.chat_id = chat_id
        if not self.state:  # make sure that data exist
            self.state="init"

    @property
    def state(self)->str:
        return bot.get_state(self.user_id, self.chat_id)
    @state.setter
    def state(self, state: str):
        bot.set_state(self.user_id, state, self.chat_id)


    def __getitem__(self, key):
        """Retrieve a value from the data storage by key using the [] syntax."""
        with bot.retrieve_data(self.user_id, self.chat_id) as storage:
            if not storage:
                return None
            return storage.get(key)
    def all(self):
        with bot.retrieve_data(self.user_id, self.chat_id) as storage:
            return storage

    def __setitem__(self, key, value):
        """Set a value  in the data storage by key using the [] syntax."""
        bot.add_data(self.user_id, self.chat_id, **{key:value})
    def set(self,**kwargs):
        bot.add_data(self.user_id, self.chat_id, **kwargs)

class BaseHMessage:
    hapi: HiddifyApi
    db: DataStorage
    chat_id: int
    user_id: int
    role:Role
    lang: str

class HMessage(types.Message,BaseHMessage):
    pass

class HCallbackQuery(types.CallbackQuery):
    message:HMessage

class HInlineQuery(types.InlineQuery,BaseHMessage):
    pass

class Middleware(handler_backends.BaseMiddleware):
    def __init__(self):
        self.update_types = ['message', 'edited_message', 'channel_post', 'edited_channel_post', 'inline_query', 'chosen_inline_result', 'callback_query', 'shipping_query', 'pre_checkout_query', 'poll', 'poll_answer', 'my_chat_member', 'chat_member', 'chat_join_request', 'message_reaction', 'message_reaction_count', 'chat_boost', 'removed_chat_boost', 'business_connection', 'business_message', 'edited_business_message', 'deleted_business_messages']
        pass
    def set_basic_elements(self,obj, data):
        user_id=chat_id=deflang=None
        base=obj
        if isinstance(obj, types.CallbackQuery):
            if not obj.message:
                return
            base=obj.message

            chat_id = base.chat.id
            user_id = obj.from_user.id
            deflang=base.from_user.language_code
        elif isinstance(obj, types.InlineQuery):
            user_id=obj.from_user.id
            deflang=obj.from_user.language_code
            base=obj
        else:
            base=obj
            chat_id = base.chat.id
            user_id = base.from_user.id
            deflang=base.from_user.language_code
        base.chat_id=chat_id
        base.user_id=user_id
        # data['lang']="en"
        base.db=db=DataStorage(user_id, chat_id)
        lang=db['lang']
        if not lang:
            lang=db['lang']=deflang
        base.lang=lang
        base.role=db['role']
        self.set_hapi(base)
        return base
    def set_user_data(self,base):
        db=base.db
        if isinstance(base,Message) and base.text and base.text.startswith("/start"):
            params = base.text.split()
            try:
                if len(params)>=2 and "admin" in params[1]:
                    uid = params[1].split("_")[1] 
                    hapi = HiddifyApi(HIDDIFYPANEL_ADMIN_LINK, uid)
                    
                    db['info']=hapi.get_admin_info()
                    db['guid']=uid
                    role=db['info']['mode']
                    if role=='super_admin':role=Role.SUPER_ADMIN
                    if role=='admin':role=Role.ADMIN
                    if role=='agent':role=Role.AGENT
                    db['admin_link']=f'{HIDDIFYPANEL_ADMIN_LINK.lstrip("/")}/{uid}/'
                    base.role=db['role']=role
                elif len(params)>=2:
                    uid=params[1]
                    base.hapi = HiddifyApi(HIDDIFYPANEL_USER_LINK, uid)
                    db['info']=base.hapi.get_user_info()
                    db['guid']=uid
                    base.role=db['role'] = Role.USER
            except Exception as e:
                logger.error(e)
                db['guid']=""
                base.role=db['role'] = Role.UNKNOWN
            self.set_hapi(base)
    def set_hapi(self,base):
        if base.role in [Role.SUPER_ADMIN,Role.ADMIN,Role.AGENT]:
            base.hapi = HiddifyApi(HIDDIFYPANEL_ADMIN_LINK, base.db['guid'])           
        else:
            base.hapi = HiddifyApi(HIDDIFYPANEL_USER_LINK, base.db['guid'])

    def pre_process(self, obj, data):
        base=self.set_basic_elements(obj,data)
        if not base:return
        self.set_user_data(base)
        
        if base.chat_id:
            bot.send_chat_action(base.chat_id,"typing")
        if isinstance(obj,Message):
            from .utils import tghelper
            tghelper.set_reaction(base)

    def post_process(self, message, data, exception):
        pass


class StorageFilter(custom_filters.AdvancedCustomFilter):
    """
    Filter to check Text message.

    .. code-block:: python3
        :caption: Example on using this filter:

        @bot.message_handler(text=['account'])
        # your function
    """

    key = 'db'

    def check(self, obj, val):
        """
        :meta private:
        """
        if isinstance(obj,Message):
            message=obj
        elif hasattr(obj,'message'):
            message=obj.message
        else:
            return 
        if not isinstance(val, dict):
            raise ValueError("Invalid Usage")
        
        storage=message.db
        for k,v in val.items():    
            l=v if isinstance(v, list) else [v]
            data=storage[k]
            for filter in l:
                if isinstance(filter,custom_filters.SimpleCustomFilter): 
                    if filter.check(data):
                        return True
                else:
                    if isinstance(filter,list) or isinstance(filter,set):
                        return data in filter
                    else:
                        return data==filter
        return False
    
    
class RoleFilter(StorageFilter):
    """
    Filter to check Text message.

    .. code-block:: python3
        :caption: Example on using this filter:

        @bot.message_handler(text=['account'])
        # your function
    """

    key = 'role'

    def check(self, obj, val):
        data={Role.USER}
        if val==Role.SUPER_ADMIN:
            data={Role.SUPER_ADMIN}
        elif val==Role.ADMIN:
            data={Role.SUPER_ADMIN,Role.ADMIN}
        elif val==Role.AGENT:
            data={Role.SUPER_ADMIN,Role.ADMIN,Role.AGENT}
        return super().check(obj,{"role":data})
            
        

class CallbackMatchFilter(custom_filters.AdvancedCustomFilter):
    

    key = 'call_action'

    def check(self, obj, val):
        if not isinstance(obj,types.CallbackQuery):
            return
        if not obj.data:return
        action= obj.data.split(":")[0]
        if isinstance(val ,list) or isinstance(val ,set):
            return action in val
        return action==val

def callback(func=None,**kwargs):
    if func is None: func=lambda call:True
    return bot.callback_query_handler_orig(func,**kwargs)
bot.callback_query_handler_orig=bot.callback_query_handler
bot.callback_query_handler=callback

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(StorageFilter())
bot.add_custom_filter(custom_filters.TextMatchFilter())
bot.add_custom_filter(CallbackMatchFilter())
bot.add_custom_filter(RoleFilter())

bot.setup_middleware(Middleware())
