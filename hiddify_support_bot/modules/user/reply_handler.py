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
import copy


@bot.message_handler(func=lambda msg: msg.sender_chat)
async def main_message_from_channel(msg: HMessage):
    # print(msg)
    newmsg = copy.deepcopy(msg)
    newmsg.reply_to_message = msg
    newmsg.main_message = msg
    newmsg.text = ""
    await is_reply_to_user_condition(newmsg)
    await reply_to_user(newmsg, add_reply_text=False)


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
        url = urlparse(msg.main_message.entities[0].url)
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
{msg.text}
        """
    # await bot.copy_message(chat_id, msg.chat.id,  msg.message_id)
    if msg.content_type != 'text':
        a = await bot.copy_message(reply_to['chat_id'], msg.chat.id,  msg.id, caption=caption, reply_parameters=ReplyParameters(reply_to['msg_id']), parse_mode='markdown',)
    else:
        await bot.send_message(reply_to['chat_id'], caption, reply_parameters=ReplyParameters(reply_to['msg_id']), parse_mode='markdown')
    msg_info = f"""[ ](https://hiddify.com/reply_to_us/?chat={reply_to['chat_id']}&msg={reply_to['msg_id']})"""
    await bot.reply_to(msg, f'{msg_info}{_("chat.reply_sent_to_user", msg.lang)}', parse_mode='markdown')


async def is_reply_to_user_condition_ignore_slash(msg: HMessage):
    return await is_reply_to_user_condition(msg, ignore_slash=True)


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
    if await msg.db.get(f"chat_data_of_+{msg.main_message.id}"):
        return True
    try:

        url = urlparse(msg.main_message.entities[0].url)
        query_params = parse_qs(url.query)
        if url.path == '/reply_to_user/':
            message_id = int(query_params.get("msg")[0])
            chat_id = int(query_params.get("chat")[0])
            user_id = int(query_params.get("user")[0])

            await msg.db.set(f"chat_data_of_+{msg.main_message.id}", {"msg_id": message_id, "chat_id": chat_id, "user_id": user_id})
            return True
    except:
        pass

    return False


@bot.message_handler(func=is_reply_to_user_condition,
                     content_types=['audio', 'photo', 'voice', 'video', 'document',
                                    'text', 'location', 'contact', 'sticker'])
async def reply_to_user(msg: HMessage, add_reply_text=True):
    reply_to_chat_data = await msg.db.get(f"chat_data_of_+{msg.main_message.id}")
    if not reply_to_chat_data:
        print("Errrorors")
        return
    user_data = await bot.get_user_data(reply_to_chat_data['user_id'], reply_to_chat_data['chat_id'])
    target_chat_lang = user_data.get('lang', 'en')

    caption = f"""[ ](https://hiddify.com/reply_to_us/?chat={msg.chat_id}&msg={msg.message_id})  
{_("chat.reply_insrtuction",target_chat_lang)}
=====
{msg.text}"""
    if msg.content_type != 'text':
        await bot.copy_message(reply_to_chat_data['chat_id'], msg.chat.id,  msg.id, reply_parameters=ReplyParameters(reply_to_chat_data['msg_id']), caption=caption, parse_mode='markdown')
    else:
        await bot.send_message(reply_to_chat_data['chat_id'], caption, reply_parameters=ReplyParameters(reply_to_chat_data['msg_id']), parse_mode='markdown')
    msg_info = f"""[ ](https://hiddify.com/reply_to_user/?chat={reply_to_chat_data['chat_id']}&user={reply_to_chat_data['user_id']}&msg={reply_to_chat_data['msg_id']})"""
    if add_reply_text:
        await bot.reply_to(msg, f'{msg_info}{_("chat.reply_sent_to_user", msg.lang)}', parse_mode='markdown')


@bot.message_handler(text_startswith="/remove", func=is_reply_to_user_condition_ignore_slash)
async def remove(msg: HMessage):
    if not msg.main_message.forward_origin:
        await bot.reply_to(msg, "select the main message")
        return
    reply_to_chat_data = await msg.db.get(f"chat_data_of_+{msg.main_message.id}")
    if not reply_to_chat_data:
        print("Errrorors")
        return

    ssh_info = ssh_utils.get_ssh_info(msg.main_message.text, searchAll=True)
    out_res = await ssh_utils.close_permission(ssh_info)

    await bot.send_message(msg.chat_id, {_("chat.removed", msg.lang)}, reply_parameters=types.ReplyParameters(msg.main_message.id), parse_mode='markdown')
    user_data = await bot.get_user_data(reply_to_chat_data['user_id'], reply_to_chat_data['chat_id'])
    target_chat_lang = user_data.get('lang', 'en')
    caption = f"""[ ](https://hiddify.com/reply_to_us/?chat={msg.chat_id}&msg={msg.message_id})
{_("chat.removed", target_chat_lang)}"""
    await bot.send_message(reply_to_chat_data['chat_id'], caption, reply_parameters=types.ReplyParameters(reply_to_chat_data['msg_id']), parse_mode='markdown')

    # print(msg.reply_to_message.forward_origin)
    # print("xxx=====", msg.main_message.forward_origin)
    orig = msg.main_message.forward_origin
    # print(orig.chat.id, orig.message_id)
    await bot.delete_message(orig.chat.id, orig.message_id)

    # await bot.delete_message(msg.main_message.chat.id, msg.main_message.id)
