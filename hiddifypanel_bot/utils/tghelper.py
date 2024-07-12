from datetime import datetime, timedelta
from hiddifypanel_bot import bot
from telebot.types import ReactionTypeEmoji, Message

from hiddifypanel_bot.hiddifyapi import api
from i18n import t as _
from .timedelta_format import format_timedelta


async def set_reaction(message: Message, emoji: str = "👍"):
    return await bot.set_message_reaction(message.chat.id, message.id, [ReactionTypeEmoji(emoji)], is_big=False)


def format_user_message(lang, user_data):

    user_data["profile_usage_current_GB"] = "{:.3f}".format(user_data.get("profile_usage_current", 0))
    user_data["profile_usage_total_GB"] = "{:.3f}".format(user_data.get("profile_usage_total", 0))

    return _("user.info", lang, **user_data)


def format_user_message_from_admin(lang, user_data):
    current_time = datetime.now()
    start_date = user_data.get("start_date")

    last_online_display = user_data.get("last_online")
    if last_online_display:
        last_online = datetime.strptime(last_online_display, "%Y-%m-%d %H:%M:%S")
        time_diff = last_online-current_time 
        user_data["last_online_relative"] = format_timedelta(time_diff, lang, granularity="minutes")
        if time_diff > timedelta(minutes=1):
            user_data["online_icon"] = "🟢"
        elif time_diff > timedelta(minutes=5):
            user_data["online_icon"] = "🟡"
        else:
            user_data["online_icon"] = "🔴"

    else:
        user_data["online_icon"] = "❌"

    user_data["current_usage_GB"] = "{:.3f}".format(user_data.get("current_usage_GB", 0))
    user_data["usage_limit_GB"] = "{:.3f}".format(user_data.get("usage_limit_GB", 0))

    if start_date:
        user_data["start_date_relative"] = format_timedelta(time_diff, lang, granularity="days")
        user_info = _("admin.userinfo_started", lang, **user_data)
    else:
        user_info = _("admin.userinfo_not_started", lang, **user_data)

    return user_info
