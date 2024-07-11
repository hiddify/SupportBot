from hiddifypanel_bot import bot, HMessage, Role
from hiddifypanel_bot.utils import tghelper
import telebot
from telebot import types
from i18n import t as _
from . import constants as C


@bot.message_handler(commands=["start"], role=Role.AGENT)
def send_welcome(msg: HMessage):
    return main_menu(msg)


@bot.message_handler(func=lambda msg: msg.text in [_("backmainmenu", msg.lang), _("mainmenu", msg.lang)], role=Role.AGENT)
def main_menu(msg: HMessage):
    text = _("admin.start", msg.lang)

    keyboards = types.InlineKeyboardMarkup()
    keyboards.add(types.InlineKeyboardButton(text=_("admin.open_admin"), web_app=types.WebAppInfo(msg.db["admin_link"])))
    keyboards.add(
        types.InlineKeyboardButton(text=_("admin.search_user"), switch_inline_query_current_chat="search "),
        types.InlineKeyboardButton(text=_("admin.add_user"), callback_data=C.ADD_USER),
    )
    keyboards.add(
        types.InlineKeyboardButton(text=_("admin.server_info"), callback_data=C.SERVER_INFO), types.InlineKeyboardButton(text=_("admin.admin_users"), callback_data=C.ADMIN_USER)
    )

    bot.reply_to(msg, text, reply_markup=keyboards)

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
