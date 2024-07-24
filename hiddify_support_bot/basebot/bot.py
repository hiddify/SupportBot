import logging
import os
import traceback
from telebot.async_telebot import logger,ExceptionHandler,types


from telebot import asyncio_filters
from telebot.asyncio_storage import StatePickleStorage
from .storage_filter import StorageFilter
from .call_action_filter import CallActionFilter
from .role_filter import RoleFilter
from .middleware import Middleware
from .hasync_telebot  import HAsyncTeleBot
from dotenv import load_dotenv
load_dotenv()
logger.setLevel(logging.INFO)  # Outputs debug messages to console.


BOT_TOKEN = os.getenv("BOT_TOKEN")

state_storage = StatePickleStorage()  # you can init here another storage



class MyExceptionHandler(ExceptionHandler):
    async def handle(self, e):
        logger.error(e)
        
        try:
           await bot.send_message(5315432352,traceback.format_exception_only(e.__class__, e))
        except:pass
        raise e
bot: HAsyncTeleBot = HAsyncTeleBot(
    BOT_TOKEN,
    exception_handler=MyExceptionHandler(),
    state_storage=state_storage,
)


bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.TextMatchFilter())
bot.add_custom_filter(asyncio_filters.TextStartsFilter())
bot.add_custom_filter(StorageFilter())
bot.add_custom_filter(CallActionFilter())
bot.add_custom_filter(RoleFilter())
bot.setup_middleware(Middleware(bot))