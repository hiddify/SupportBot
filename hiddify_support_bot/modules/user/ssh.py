import asyncio
from hiddify_support_bot import bot, HMessage, HCallbackQuery, Role
from hiddify_support_bot.utils import start_param, tghelper
import telebot
from telebot import types
from i18n import t as _
from . import constants as C
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ForceReply, ReplyKeyboardRemove, Message
import os
from . import ssh_utils
from io import StringIO

SSH_HOST = os.environ.get("SSH_HOST")

@bot.message_handler(text_startswith="/get_ssh_link")
async def get_ssh_link(msg: HMessage):    
    langs=['en','fa']
    bot_username=(await bot.get_me()).username
    if not msg.reply_to_message or not msg.reply_to_message.sender_chat:
        await bot.reply_to(msg,"error!e12")
        return 
    cid=msg.reply_to_message.sender_chat.id
    for lang in langs:
        sp=start_param.encode("ssh",{'cid':cid,'lang':lang})        
        txt=f"{lang}\n\nhttps://t.me/{bot_username}?start={sp}"
        await bot.reply_to(msg,txt)

@bot.message_handler(text_startswith="/start ssh")
async def send_ssh(msg: HMessage,start_action=None,start_params=None):
    if start_action and start_action!="ssh":
        await bot.reply_to(msg,"invalid!E1")
        return
    if start_params:
        cid=start_params['cid']
        await msg.db.set(ssh_target_chat_id=cid)
    markup = ForceReply(selective=False)
    
    await bot.send_message(msg.chat.id, _("ssh.welcome",msg.lang), parse_mode='markdown')
    await bot.send_message(msg.chat.id, _("ssh.add_permission",msg.lang, public_key=ssh_utils.SSH_PUB_STR), parse_mode='markdown')

    await bot.send_message(msg.chat.id, _("ssh.send_ssh",msg.lang), reply_markup=markup, parse_mode='markdown')
    await bot.register_next_step_handler(msg.user_id, msg.chat_id, ssh_received)


@bot.step_handler()
async def ssh_received(msg: HMessage):
    ssh_info = ssh_utils.get_ssh_info(msg.text)
    panel_version = await ssh_utils.test_ssh_connection(ssh_info)
    if not panel_version:
        print("""We can not connect to your server. """)
        await bot.send_message(msg.chat.id, _("ssh.connection_failed",msg.lang))
        await bot.send_chat_action(msg.chat_id,"typing")
        await asyncio.sleep(1)
        return await send_ssh(msg,)

    await bot.send_message(msg.chat.id, _("ssh.connection_success",msg.lang, panel_version=panel_version))
    await msg.db.set(SSH_info=ssh_info, panel_version=panel_version)
    await bot.register_next_step_handler(msg.user_id, msg.chat_id, ssh_received_comment)


@bot.step_handler()
async def ssh_received_comment(msg:HMessage):
    ssh_info = await msg.db['SSH_info']
    panel_version = await msg.db['panel_version']
    
    msgtxt = f'''[ ](https://hiddify.com/reply_to_user/?chat={msg.chat.id}&user={msg.from_user.id}&msg={msg.id})
    [{msg.from_user.first_name or ""} {msg.from_user.last_name or ""}](tg://user?id={msg.from_user.id}) [user:](@{msg.from_user.username})  in {msg.chat.title}
    {panel_version}
    `ssh {ssh_info['user']}@{ssh_info['host']} -p {ssh_info['port']}`
    [SSH Site](https://{SSH_HOST}/?host={ssh_info['host']}&port={ssh_info['port']}&user={ssh_info['user']}&password=support)

    {msg.text or msg.caption}
    '''
    ssh_target_chat_id=await msg.db.get('ssh_target_chat_id',-1001834220158)
    # print(msgtxt)
    if msg.text:
        new_message = await bot.send_message(ssh_target_chat_id, msgtxt, parse_mode='markdown')
        
    else:
        new_message = await bot.copy_message(ssh_target_chat_id,msg.chat_id,msg.id, msgtxt, parse_mode='markdown')    

    # data['SSH_info_comment'] = message
    # new_message=await bot.forward_message(-1001834220158,from_chat_id=message.chat.id,message_id=message.message_id)
    await bot.send_message(msg.chat.id, _("ssh.finish",msg.lang), parse_mode='markdown')

    # new_message = await bot.send_message(-1001834220158, msgtxt, parse_mode='markdown')

    await bot.send_message(msg.chat.id, _("ssh.remove_permission",msg.lang,public_key=ssh_utils.SSH_PUB_STR), parse_mode='markdown')