from telebot import types
from . import DataStorage,Role

class BaseHMessage:
    db: DataStorage
    common_db: DataStorage
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
