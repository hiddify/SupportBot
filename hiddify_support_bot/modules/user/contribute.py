from hiddify_support_bot import bot,HMessage,Role
from hiddify_support_bot.utils import tghelper,start_param
import telebot
from i18n import t as _

@bot.message_handler(text_startswith="/start contribute")
async def send_welcome(msg:HMessage,start_action,start_params):
    if start_action!="contribute":
        return bot.reply_to(msg,"error")
    
    
    chat_id,msg_id=int(start_params['cid']),int(start_params['mid'])
    
    user_data=await bot.get_user_data(msg_id,chat_id=chat_id)
    welcome_note=user_data.get("welcome_note")
    if not welcome_note:
            await bot.reply_to(msg, _("contribute.invalid",msg.lang),parse_mode="markdown")            
            return
    lang_wn=welcome_note.get(msg.lang)
    if not lang_wn:
        for k in welcome_note:
            lang_wn=welcome_note[k]
            break
    
    await msg.db.set(reply_to_us={"msg_id":msg_id,"chat_id":chat_id})
    await bot.reply_to(msg, f"[ ](https://hiddify.com/reply_to_us/?chat={msg.chat_id}&msg={msg.message_id}){lang_wn}",parse_mode="markdown")    
    
    

    # await bot.delete_my_commands(scope=None, language_code=None)

    # await bot.set_my_commands(
    #     commands=[
    #         telebot.types.BotCommand("command1", "command1 description"),
    #         telebot.types.BotCommand("command2", "command2 description")
    #     ],
    #     # scope=telebot.types.BotCommandScopeChat(12345678)  # use for personal command menu for users
    #     # scope=telebot.types.BotCommandScopeAllPrivateChats()  # use for all private chats
    # )
    
    # cmd = await bot.get_my_commands(scope=None, language_code=None)
    # print([c.to_json() for c in cmd])


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
# @bot.message_handler(func=lambda message: True)
# async def echo_message(message):
    
#     await tghelper.set_reaction(message)
#     await bot.reply_to(message, message.text)




