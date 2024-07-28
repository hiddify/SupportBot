import asyncio
from hiddify_support_bot import bot, HMessage, HCallbackQuery, Role
from hiddify_support_bot.utils import tghelper
import telebot
from telebot import types
from i18n import t as _
from . import constants as C
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ForceReply, ReplyKeyboardRemove, Message, ReplyParameters
import os
from . import ssh_utils
from io import StringIO
from urllib.parse import urlparse, parse_qs


async def is_reply_to_us_condition(msg: HMessage, ignore_slash=False):
    if not msg or not msg.chat or not msg.from_user:
        return False
    if not ignore_slash and msg.text.startswith("/"):
        return False
    if msg.from_user.id != msg.chat.id:
        return False
    if not msg.reply_to_message:
        if await msg.db.get('reply_to_us'):
            return True
        return False

    try:
        url = urlparse(msg.reply_to_message.entities[0].url)
        query_params = parse_qs(url.query)
        if url.path == '/reply_to_us/':
            message_id = int(query_params.get("msg")[0])
            chat_id = int(query_params.get("chat")[0])

            await msg.db.set(reply_to_us={"msg_id": message_id, "chat_id": chat_id})
    except Exception as e:
        return False

    return True


@bot.message_handler(func=is_reply_to_us_condition, content_types=['audio', 'photo', 'voice', 'video', 'document',
                                                                   'text', 'location', 'contact', 'sticker'])
async def reply_to_us(msg: HMessage):
    reply_to = await msg.db.get('reply_to_us')
    if not reply_to:
        print("EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEror")
        return

    caption = f"""[ ](https://hiddify.com/reply_to_user/?chat={msg.chat.id}&user={msg.from_user.id}&msg={msg.id})
`{msg.from_user.id}` `{msg.chat.id}` 
[{msg.from_user.first_name or ""} {msg.from_user.last_name or ""}](tg://user?id={msg.from_user.id})            
======
{msg.text or msg.caption}
        """
    # await bot.copy_message(chat_id, msg.chat.id,  msg.message_id)
    if msg.text:
        await bot.send_message(reply_to['chat_id'], caption, reply_parameters=ReplyParameters(reply_to['msg_id']), parse_mode='markdown')
    else:
        await bot.copy_message(reply_to['chat_id'], msg.chat.id,  msg.message_id, caption=caption, reply_parameters=ReplyParameters(reply_to['msg_id']), parse_mode='markdown',)


async def is_reply_to_user_condition_ignore_slash(msg: HMessage):
    return is_reply_to_user_condition(msg: HMessage, ignore_slash=True):
    

async def is_reply_to_user_condition(msg: HMessage, ignore_slash=False):
    if not msg:
        return False
    if not msg.chat or not msg.from_user:
        return False
    if not msg.reply_to_message:
        return False
    if msg.from_user.id == msg.chat.id:
        return False
    if not ignore_slash and msg.text.startswith("/"):
        return False
    if await msg.db.get(f"chat_data_of_+{msg.reply_to_message.id}"):
        return True
    try:
        url = urlparse(msg.reply_to_message.entities[0].url)
        query_params = parse_qs(url.query)
        if url.path == '/reply_to_user/':
            message_id = int(query_params.get("msg")[0])
            chat_id = int(query_params.get("chat")[0])
            user_id = int(query_params.get("user")[0])

            await msg.db.set(f"chat_data_of_+{msg.reply_to_message.id}", {"msg_id": message_id, "chat_id": chat_id, "user_id": user_id})
            return True
    except:
        pass

    return False


@bot.message_handler(func=is_reply_to_user_condition,
                     content_types=['audio', 'photo', 'voice', 'video', 'document',
                                    'text', 'location', 'contact', 'sticker'])
async def reply_to_user(msg: HMessage):
    reply_to_chat_data = await msg.db.get(f"chat_data_of_+{msg.reply_to_message.id}")
    if not reply_to_chat_data:
        print("Errrorors")
        return
    user_data = await bot.get_user_data(reply_to_chat_data['user_id'], reply_to_chat_data['chat_id'])
    target_chat_lang = user_data.get('lang', 'en')

    caption = f"""[ ](https://hiddify.com/reply_to_us/?chat={msg.chat_id}&msg={msg.message_id})  
{_("chat.reply_insrtuction",target_chat_lang)}
=====
{msg.text or msg.caption}"""
    if msg.text:
        await bot.send_message(reply_to_chat_data['chat_id'], caption, reply_parameters=ReplyParameters(reply_to_chat_data['msg_id']), parse_mode='markdown')
    else:
        await bot.copy_message(reply_to_chat_data['chat_id'], msg.chat.id,  msg.id, reply_parameters=ReplyParameters(reply_to_chat_data['msg_id']), caption=caption, parse_mode='markdown')
        await bot.reply_to(msg, _("chat.reply_sent_to_user", msg.lang), parse_mode='markdown')
