from hiddify_support_bot import *
from hiddify_support_bot.utils import tghelper
import telebot
from telebot import types
from i18n import t as _

@bot.message_handler(func=lambda msg: not msg.via_bot and (not msg.sender_chat or msg.sender_chat.type!="channel"))
async def default_response(msg:HMessage):
    
    await bot.reply_to(msg, _("invalid_request"))

@bot.callback_query_handler(func=lambda message: True)
async def default_response(callback:HCallbackQuery):
    if callback.message:
       await bot.answer_callback_query(callback.message.chat_id,callback.id,_("invalid_request"))
    
@bot.inline_handler(lambda query: True)
async def default_response(query:HInlineQuery):
    # bot.answer_inline_query(query.id,results=[types.InlineQueryResultArticle("inline.invalid"+query.query,title=_('inline.invalid_query'),input_message_content=types.InputTextMessageContent(_('inline.invalid_query')))],cache_time=0)
    await bot.answer_inline_query(query.id,results=[],cache_time=0)

    