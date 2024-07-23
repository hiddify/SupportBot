from hiddify_support_bot import bot,HMessage,Role
from hiddify_support_bot.utils import start_param
import telebot
from i18n import t as _

@bot.message_handler(commands=["welcome"])
async def set_welcome(msg:HMessage):
    if not msg.reply_to_message or not msg.reply_to_message.sender_chat or msg.reply_to_message.sender_chat.type!="channel":
        await bot.reply_to(msg,_("actions.setwelcome.invalid",msg.lang))
        return 
    welcome_note=msg.text.removeprefix("/welcome").strip()
    lang="en"
    if len(welcome_note.split()[0])==2:
        lang=welcome_note.split()[0]
        welcome_note=welcome_note.removeprefix(lang).strip()
    data=await bot.get_user_data(msg.reply_to_message.id,msg.chat.id)
    allwelcome= data.get('welcome_note',{})
    allwelcome[lang]=welcome_note
    await bot.add_user_data(msg.reply_to_message.id,msg.chat.id,welcome_note=allwelcome)
    await bot.reply_to(msg, _("actions.setwelcome_success",msg.lang))    
    

@bot.message_handler(commands=["get_link"])
async def set_welcome(msg:HMessage):
    if not msg.reply_to_message or not msg.reply_to_message.sender_chat or msg.reply_to_message.sender_chat.type!="channel":
        await bot.reply_to(msg,_("actions.setwelcome.invalid",msg.lang))
        return 
    
    data=await bot.get_user_data(msg.reply_to_message.id,msg.chat.id)
    allwelcome= data.get('welcome_note',{})
    bot_username=(await bot.get_me()).username
    for lang,note in allwelcome.items():
        sp=start_param.encode("contribute",{'cid':msg.chat.id,'mid':msg.reply_to_message.id,'lang':lang})        
        txt=f"https://t.me/{bot_username}?start={sp}\n__{lang}__\n{note}"
        await bot.reply_to(msg,txt )    
    

