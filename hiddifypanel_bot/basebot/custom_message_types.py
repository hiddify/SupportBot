from telebot import types
from . import DataStorage,Role
from hiddifypanel_bot.hiddifyapi import HiddifyApi
class BaseHMessage:
    hapi: "HiddifyApi"
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
