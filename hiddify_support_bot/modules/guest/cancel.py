from hiddify_support_bot import bot,HMessage,Role
from hiddify_support_bot.utils import tghelper
import telebot
from i18n import t as _

@bot.message_handler(state="*", commands=['cancel'])
async def any_state(message):
    """
    Cancel state
    """
    await bot.send_message(message.chat.id, _("chat.canceled"))
    await bot.delete_state(message.from_user.id, message.chat.id)
    # await send_welcome(message)