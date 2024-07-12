from hiddifypanel_bot import *
from hiddifypanel_bot.utils import tghelper

import telebot
from telebot.types import ReplyParameters, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup,WebAppInfo
from . import constants as C
import i18n


@bot.callback_query_handler(call_action=C.ADD_USER, role=Role.AGENT)
async def add_user_handler(call: HCallbackQuery):
    await add_user_name(call.message)
    await bot.answer_callback_query(call.id)


async def add_user_name(msg: HMessage):
    resp = i18n.t("addname", msg.lang)
    await bot.reply_to(msg, resp, reply_markup=ForceReply(False, resp))
    await bot.register_next_step_handler(msg.user_id,msg.chat_id, add_user_package_days)

@bot.step_handler()
async def add_user_package_days(msg: HMessage):
    name = msg.text
    resp = i18n.t("adddays", msg.lang)
    await bot.reply_to(msg, resp, reply_markup=ForceReply(False, resp))
    await bot.register_next_step_handler(msg.user_id,msg.chat_id, validate_package_days, name)

@bot.step_handler()
async def validate_package_days(msg: HMessage, name: str):
    if msg.text.isnumeric():
        package_days = int(msg.text)
        resp = i18n.t("addgb", msg.lang)
        await bot.reply_to(msg, resp, reply_markup=ForceReply(False, resp))
        await bot.register_next_step_handler(msg.user_id,msg.chat_id, validate_usage_limit, name, package_days)
    else:
        await bot.reply_to(msg, i18n.t("invaliddays", msg.from_user.language_code))
        await bot.register_next_step_handler(msg.user_id,msg.chat_id, validate_package_days, name)

@bot.step_handler()
async def validate_usage_limit(msg: HMessage, name: str, package_days: int):
    try:
        usage_limit = float(msg.text)
        await add_user_complete(msg, name, package_days, usage_limit)
    except ValueError:
        resp = i18n.t("invalidgb", msg.lang)
        await bot.reply_to(msg, resp, reply_markup=ForceReply(False, resp))
        await bot.register_next_step_handler(msg.user_id,msg.chat_id, validate_usage_limit, name, package_days)

@bot.step_handler()
async def add_user_complete(msg: HMessage, name: str, package_days: int, usage_limit: float):

    user_data = await msg.hapi.add_user(User(
        comment="",
         name= name,
          package_days= package_days,
           usage_limit_GB= usage_limit
    ))
    if "msg" not in user_data:
        user_info=await msg.hapi.get_user_info(user_data['uuid'])
        resp=tghelper.format_user_message(msg.lang,user_info)
        uuid = user_data.get("uuid", "N/A")
        sublink_data = user_info['profile_url']
        qr_code = msg.hapi.generate_qr_code(sublink_data)

        inline_keyboard = InlineKeyboardMarkup()
        # inline_keyboard.add(InlineKeyboardButton(text="Open Sublink", web_app=WebAppInfo(sublink_data)))
        inline_keyboard.add(InlineKeyboardButton(text="Open Sublink", url=sublink_data))
        
        await bot.send_photo(msg.chat.id, qr_code, caption=resp, reply_markup=inline_keyboard)
        # else:
        #     bot.reply_to(message, "Failed to retrieve user data.")
    else:
        await bot.reply_to(msg, "Failed to add user.")
