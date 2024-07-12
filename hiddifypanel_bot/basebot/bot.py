import logging
import os
from telebot.async_telebot import logger
from telebot import TeleBot, ExceptionHandler,types
from telebot import asyncio_filters
from telebot.asyncio_storage import StateMemoryStorage
from .storage_filter import StorageFilter
from .call_action_filter import CallActionFilter
from .role_filter import RoleFilter
from .middleware import Middleware
from .hasync_telebot  import HAsyncTeleBot
logger.setLevel(logging.INFO)  # Outputs debug messages to console.


BOT_TOKEN = os.getenv("BOT_TOKEN")

state_storage = StateMemoryStorage()  # you can init here another storage


class MyExceptionHandler(ExceptionHandler):
    def handle(self, exception):
        logger.error(exception)
        raise exception

bot: HAsyncTeleBot = HAsyncTeleBot(
    BOT_TOKEN,
    exception_handler=MyExceptionHandler(),
    state_storage=state_storage,
)


bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.TextMatchFilter())
bot.add_custom_filter(StorageFilter())
bot.add_custom_filter(CallActionFilter())
bot.add_custom_filter(RoleFilter())
bot.setup_middleware(Middleware(bot))