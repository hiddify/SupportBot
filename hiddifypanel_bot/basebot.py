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
        if not self.get_state():  # make sure that data exist
            self.set_state("init")

    def get_state(self):
        return bot.get_state(self.user_id, self.chat_id)

    def set_state(self, state):
        return bot.set_state(self.user_id, state, self.chat_id)

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


class HMessage(types.Message):
    hapi: HiddifyApi
    db: DataStorage
    chat_id: int
    user_id: int
    role:Role
    lang: str
    @property
    def state(self)->str:
        return self.storage.get_state()
    @state.setter
    def state(self, value: str):
        self.storage.set_state(value)

class HCallbackQuery(types.CallbackQuery):
    message:HMessage

class Middleware(handler_backends.BaseMiddleware):
    def __init__(self):
        self.update_types = ["message","callback_query"]
        pass

    def pre_process(self, obj:Message|types.CallbackQuery, data):
        if isinstance(obj, types.CallbackQuery):
            message=obj.message
            message.chat_id = message.chat.id
            message.user_id = obj.from_user.id
        else:
            message=obj
            message.chat_id = message.chat.id
            message.user_id = message.from_user.id
        
        # data['lang']="en"
        db=DataStorage(message.user_id, message.chat_id)
        lang=db['lang']
        if not lang:
            lang=db['lang']=message.from_user.language_code
        
        message.role=db['role']

        if message and message.text and message.text.startswith("/start"):
            params = message.text.split()
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
                    message.role=db['role']=role
                elif len(params)>=2:
                    uid=params[1]
                    message.hapi = HiddifyApi(HIDDIFYPANEL_USER_LINK, uid)
                    db['info']=message.hapi.get_user_info()
                    db['guid']=uid
                    message.role=db['role'] = Role.USER
            except Exception as e:
                logger.error(e)
                db['guid']=""
                message.role=db['role'] = Role.UNKNOWN
                
        if message.role in [Role.SUPER_ADMIN,Role.ADMIN,Role.AGENT]:
            message.hapi = HiddifyApi(HIDDIFYPANEL_ADMIN_LINK, db['guid'])           
        else:
            message.hapi = HiddifyApi(HIDDIFYPANEL_USER_LINK, db['guid'])
        message.db=db
        message.lang=lang
        bot.send_chat_action(message.chat_id,"typing")
        from .utils import tghelper
        tghelper.set_reaction(message)

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

    def check(self, message:HMessage, val):
        """
        :meta private:
        """
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
    
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(StorageFilter())

bot.setup_middleware(Middleware())
