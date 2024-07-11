from hiddifypanel_bot import bot, HMessage, HCallbackQuery, Role
from hiddifypanel_bot.utils import tghelper
import telebot
from telebot import types
from i18n import t as _
from . import constants as C


@bot.message_handler(role=Role.USER)
def send_welcome(msg: HMessage):

    text = _("start", msg.lang)
    info = msg.hapi.get_user_info()

    # bot.reply_to(msg, text+str(info))
    show_user(msg)


def show_user(msg: HMessage, edit=False):

    user_data = msg.hapi.get_user_info()
    if user_data["lang"] == msg.lang:
        msg.lang = msg.db["lang"] = user_data["lang"]

    if user_data:
        restext = tghelper.format_user_message(msg, user_data)

        sublink = user_data["profile_url"]
        qr_code = msg.hapi.generate_qr_code(sublink)

        unauthorized_keyboard = types.InlineKeyboardMarkup()
        unauthorized_keyboard.add(types.InlineKeyboardButton(text=_("user.open_sublink"), web_app=types.WebAppInfo(sublink)))
        unauthorized_keyboard.add(types.InlineKeyboardButton(text=_("user.update"), callback_data="user.update"))

        if edit:
            try:  # it raise error if no change happens
                bot.edit_message_caption(restext, msg.chat_id, message_id=msg.message_id, reply_markup=unauthorized_keyboard)
            except:
                pass
        else:
            bot.send_photo(msg.chat_id, qr_code, caption=restext, reply_markup=unauthorized_keyboard, protect_content=True)

        if user_data["telegram_id"] == msg.user_id:
            msg.hapi.update_my_user({"telegram_id", msg.user_id})
    else:
        bot.reply_to(msg, _("user.not_found"))


@bot.callback_query_handler(call_action=C.USER_UPDATE)
def update_user(call: HCallbackQuery):
    show_user(call.message, edit=True)
    bot.answer_callback_query(call.id)
