from hiddifypanel_bot import bot,HiddifyApi
from hiddifypanel_bot.utils import tghelper
import telebot
from i18n import t as _

@bot.message_handler(commands=['start'])
def send_welcome(message,lang,hapi:HiddifyApi):
    
    text = _('start',lang)
    bot.reply_to(message, text)
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




