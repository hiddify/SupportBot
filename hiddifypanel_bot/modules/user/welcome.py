from hiddifypanel_bot import bot, HMessage, HCallbackQuery, Role
from hiddifypanel_bot.utils import tghelper
import telebot
from telebot import types
from i18n import t as _
from . import constants as C


@bot.message_handler(role=Role.USER)
async def send_welcome(msg: HMessage):

    text = _("start", msg.lang)
    info = await msg.hapi.get_user_info()

    # bot.reply_to(msg, text+str(info))
    await show_user(msg)
    await bot.delete_message(msg.chat_id,msg.id)


async def show_user(msg: HMessage, edit=False):

    user_data = await msg.hapi.get_user_info()
    if user_data["lang"] == msg.lang:
        msg.lang = msg.db["lang"] = user_data["lang"]

    if user_data:
        restext = tghelper.format_user_message(msg, user_data)

        sublink = user_data["profile_url"]
        

        unauthorized_keyboard = types.InlineKeyboardMarkup()
        unauthorized_keyboard.add(types.InlineKeyboardButton(text=_("user.open_sublink"), web_app=types.WebAppInfo(sublink)))
        unauthorized_keyboard.add(types.InlineKeyboardButton(text=_("user.update"), callback_data="user.update"))
        # unauthorized_keyboard.add(types.InlineKeyboardButton(text="Open Sublink", url=sublink))

        if edit:
            try:  # it raise error if no change happens
                await bot.edit_message_caption(restext, msg.chat_id, message_id=msg.message_id, reply_markup=unauthorized_keyboard)
            except:
                pass
        else:
            qr_code = msg.hapi.generate_qr_code(sublink)
            await bot.send_photo(msg.chat_id, qr_code, caption=restext, reply_markup=unauthorized_keyboard, protect_content=True)

        if user_data["telegram_id"] == msg.user_id:
            await msg.hapi.update_my_user({"telegram_id", msg.user_id})
    else:
        await bot.reply_to(msg, _("user.not_found"))


@bot.callback_query_handler(call_action=C.USER_UPDATE)
async def update_user(call: HCallbackQuery):
    await show_user(call.message, edit=True)
    await bot.answer_callback_query(call.id)
    await bot.send_chat_action(call.message.chat_id,"")
