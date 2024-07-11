from hiddifypanel_bot import bot,HiddifyApi
from hiddifypanel_bot.utils import tghelper

import telebot
from telebot.types import ReplyParameters,ForceReply,InlineKeyboardButton,InlineKeyboardMarkup

import i18n

@bot.message_handler(commands="add")
def add_user_name(message,lang,hapi):
    resp=i18n.t("addname",lang)
    bot.reply_to(message, resp,reply_markup=ForceReply(False,resp))
    bot.register_next_step_handler(message, add_user_package_days,lang,hapi)

def add_user_package_days(message,lang,hapi):
    name = message.text
    resp=i18n.t("adddays",lang)
    bot.reply_to(message, resp,reply_markup=ForceReply(False,resp))
    bot.register_next_step_handler(message, validate_package_days, lang,hapi,name)

def validate_package_days(message,  lang,hapi,name:str):
    if message.text.isnumeric():
        package_days = int(message.text)
        resp=i18n.t("addgb",lang)
        bot.reply_to(message, resp,reply_markup=ForceReply(False,resp))
        

        bot.register_next_step_handler(message, validate_usage_limit,lang,hapi, name, package_days)
    else:
        bot.reply_to(message, i18n.t("invaliddays",message.from_user.language_code))
        bot.register_next_step_handler(message, validate_package_days,lang,hapi, name)

def validate_usage_limit(message,lang,hapi, name:str, package_days:int):
    try:
        usage_limit = float(message.text)
        add_user_complete(message, lang,hapi,name, package_days, usage_limit)
    except ValueError:
        resp=i18n.t("invalidgb",lang)
        bot.reply_to(message, resp,reply_markup=ForceReply(False,resp))
        bot.register_next_step_handler(message, validate_usage_limit,lang,hapi, name, package_days)

def add_user_complete(message, lang,hapi:HiddifyApi,name:str, package_days:int, usage_limit:float):
    
    user_data = hapi.add_service("", name, package_days, usage_limit)
    if 'msg' not in user_data:
        uuid=user_data.get('uuid', 'N/A')
        sublink_data = f"test/{uuid}"
        qr_code = hapi.generate_qr_code(sublink_data)
        
        user_info = (
            f"User UUID: {uuid}\n"
            f"Name: {user_data.get('name', 'N/A')}\n"
            f"Usage Limit: {user_data.get('usage_limit_GB', 'N/A')} GB\n"
            f"Package Days: {user_data.get('package_days', 'N/A')} Days"
        )
        inline_keyboard = InlineKeyboardMarkup()
        inline_keyboard.add(InlineKeyboardButton(text="Open Sublink", web_app=sublink_data))
        
        bot.send_photo(message.chat.id, qr_code, caption=user_info, reply_markup=inline_keyboard)
        # else:
        #     bot.reply_to(message, "Failed to retrieve user data.")
    else:
        bot.reply_to(message, "Failed to add user.")


