from hiddifypanel_bot import *
from hiddifypanel_bot.utils import tghelper

import telebot
from telebot.types import ReplyParameters, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from . import constants as C
import i18n


@bot.callback_query_handler(call_action=C.ADD_USER, role=Role.AGENT)
def add_user_handler(call: HCallbackQuery):
    add_user_name(call.message)
    bot.answer_callback_query(call.id)


def add_user_name(msg: HMessage):
    resp = i18n.t("addname", msg.lang)
    bot.reply_to(msg, resp, reply_markup=ForceReply(False, resp))
    bot.register_next_step_handler(msg, add_user_package_days)


def add_user_package_days(msg: HMessage):
    name = msg.text
    resp = i18n.t("adddays", msg.lang)
    bot.reply_to(msg, resp, reply_markup=ForceReply(False, resp))
    bot.register_next_step_handler(msg, validate_package_days, name)


def validate_package_days(msg: HMessage, name: str):
    if msg.text.isnumeric():
        package_days = int(msg.text)
        resp = i18n.t("addgb", msg.lang)
        bot.reply_to(msg, resp, reply_markup=ForceReply(False, resp))
        bot.register_next_step_handler(msg, validate_usage_limit, name, package_days)
    else:
        bot.reply_to(msg, i18n.t("invaliddays", msg.from_user.language_code))
        bot.register_next_step_handler(msg, validate_package_days, name)


def validate_usage_limit(msg: HMessage, name: str, package_days: int):
    try:
        usage_limit = float(msg.text)
        add_user_complete(msg, name, package_days, usage_limit)
    except ValueError:
        resp = i18n.t("invalidgb", msg.lang)
        bot.reply_to(msg, resp, reply_markup=ForceReply(False, resp))
        bot.register_next_step_handler(msg, validate_usage_limit, name, package_days)


def add_user_complete(msg: HMessage, name: str, package_days: int, usage_limit: float):

    user_data = msg.hapi.add_service("", name, package_days, usage_limit)
    if "msg" not in user_data:
        uuid = user_data.get("uuid", "N/A")
        sublink_data = f"test/{uuid}"
        qr_code = msg.hapi.generate_qr_code(sublink_data)

        user_info = (
            f"User UUID: {uuid}\n"
            f"Name: {user_data.get('name', 'N/A')}\n"
            f"Usage Limit: {user_data.get('usage_limit_GB', 'N/A')} GB\n"
            f"Package Days: {user_data.get('package_days', 'N/A')} Days"
        )
        inline_keyboard = InlineKeyboardMarkup()
        inline_keyboard.add(InlineKeyboardButton(text="Open Sublink", web_app=sublink_data))

        bot.send_photo(msg.chat.id, qr_code, caption=user_info, reply_markup=inline_keyboard)
        # else:
        #     bot.reply_to(message, "Failed to retrieve user data.")
    else:
        bot.reply_to(msg, "Failed to add user.")
