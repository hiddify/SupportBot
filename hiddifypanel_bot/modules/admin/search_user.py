from datetime import datetime
from hiddifypanel_bot import *
from hiddifypanel_bot.utils import tghelper
import telebot
from telebot import types
from i18n import t as _
from . import constants as C


@bot.inline_handler(lambda query: query.query.startswith("search"), role=Role.AGENT)
def handle_inline_query(query: HInlineQuery):
    search_query = query.query.lstrip("search").strip()
    results = inline_query(query, search_query)
    button = types.InlineQueryResultsButton(_("admin.search_in_web"), types.WebAppInfo(query.db["admin_link"] + "/admin/user/?search=" + search_query))
    if results:
        next_offset = int(query.offset or "0") + 50 if len(results) >= 50 else None
        bot.answer_inline_query(query.id, results, is_personal=True, next_offset=next_offset, button=button)
    else:
        bot.answer_inline_query(query.id, results, is_personal=True, button=button)


def inline_query(query: HInlineQuery, name: str):
    results = []
    offset = int(query.offset or "0")
    user_list = query.hapi.get_user_list_by_name(name, offset, 50)

    if user_list:
        for user in user_list:
            resp = tghelper.format_user_message_from_admin(query.lang, user)

            response_text = f'`{user["uuid"]}`\n' + resp
            response_text = response_text.replace(".", "\\.")
            keyboards = types.InlineKeyboardMarkup()
            keyboards.add(types.InlineKeyboardButton(text=_("admin.loading"), callback_data="user_" + user["uuid"]))

            article = types.InlineQueryResultArticle(
                id=user["uuid"],
                title=user["name"],
                description=resp,
                # url=subscription_link,
                reply_markup=keyboards,
                input_message_content=types.InputTextMessageContent(response_text, parse_mode="MarkdownV2"),
            )
            results.append(article)
    return results
