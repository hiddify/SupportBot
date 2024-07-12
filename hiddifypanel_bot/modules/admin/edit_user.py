from datetime import datetime
from hiddifypanel_bot import *
from hiddifypanel_bot.utils import tghelper
import telebot
from telebot import types
from i18n import t as _


from . import constants as C


def filter_for_via_bot(msg: HMessage):
    if not msg.via_bot:
        return
    if not msg.reply_markup:
        return
    if len(msg.reply_markup.keyboard) != 1:
        return
    key = msg.reply_markup.keyboard[0][0]
    if not key.callback_data:
        return
    if not key.callback_data.startswith("user_"):
        return
    return True


@bot.message_handler(func=filter_for_via_bot)
async def user_resp_from_inline_query(msg: HMessage):
    key = msg.reply_markup.keyboard[0][0]
    uuid = key.callback_data.split("_")[-1]
    await bot.delete_message(msg.chat_id, msg.message_id)
    user = await msg.hapi.get_user(uuid)
    await send_user_info(msg, user)


async def send_user_info(msg:HMessage, user: User):
    resp = tghelper.format_user_message_from_admin(msg.lang, user)
    keyboards = types.InlineKeyboardMarkup()
    keyboards.add(
        types.InlineKeyboardButton(text=_("admin.open_admin"), web_app=types.WebAppInfo(f"{msg.hapi.get_admin_link()}/admin/user/edit/?id={user['id']}")),
        types.InlineKeyboardButton(text=_("admin.search_user"), switch_inline_query_current_chat="search "),
    )
    enable_key = types.InlineKeyboardButton(text=_("admin.user.enable"), callback_data=f"{C.USER_ENABLE}:{user['uuid']}")
    if user["enable"]:
        enable_key = types.InlineKeyboardButton(text=_("admin.user.disable"), callback_data=f"{C.USER_DISABLE}:{user['uuid']}")
    keyboards.add(enable_key, types.InlineKeyboardButton(text=_("admin.user.delete"), callback_data=f"{C.USER_DELETE}:{user['uuid']}"))
    keyboards.add(
        types.InlineKeyboardButton(text=_("admin.user.reset_days"), callback_data=f"{C.USER_RESET_DAYS}:{user['uuid']}"),
        types.InlineKeyboardButton(text=_("admin.user.reset_usage"), callback_data=f"{C.USER_RESET_USAGE}:{user['uuid']}"),
    )

    await bot.send_message(msg.chat_id, resp, reply_markup=keyboards)


@bot.callback_query_handler(call_action=C.USER_ENABLE, role=Role.AGENT)
async def enable_user_handler(call: HCallbackQuery):
    uuid = call.data.split(":")[-1]
    user = await call.message.hapi.update_user(uuid, {"enable": True})
    await send_user_info(call.message, user)
    await bot.delete_message(call.message.chat_id, call.message.id)
    await bot.answer_callback_query(call.id)


@bot.callback_query_handler(call_action=C.USER_ENABLE, role=Role.AGENT)
async def enable_user_handler(call: HCallbackQuery):
    uuid = call.data.split(":")[-1]
    user = await call.message.hapi.update_user(uuid, {"enable": True})
    await send_user_info(call.message, user)
    await bot.delete_message(call.message.chat_id, call.message.id)
    await bot.answer_callback_query(call.id)
