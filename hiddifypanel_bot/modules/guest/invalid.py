from hiddifypanel_bot import *
from hiddifypanel_bot.utils import tghelper
import telebot
from telebot import types
from i18n import t as _

@bot.message_handler(func=lambda message: not message.via_bot)
def default_response(msg:HMessage):
    bot.reply_to(msg, _("invalid_request"))

@bot.callback_query_handler(func=lambda message: True)
def default_response(callback:HCallbackQuery):
    if callback.message:
        bot.answer_callback_query(callback.message.chat_id,callback.id,_("invalid_request"))
    
@bot.inline_handler(lambda query: True)
def default_response(query:HInlineQuery):
    # bot.answer_inline_query(query.id,results=[types.InlineQueryResultArticle("inline.invalid"+query.query,title=_('inline.invalid_query'),input_message_content=types.InputTextMessageContent(_('inline.invalid_query')))],cache_time=0)
    bot.answer_inline_query(query.id,results=[],cache_time=0)