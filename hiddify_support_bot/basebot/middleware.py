from asyncio.log import logger
import os
import re
from telebot import asyncio_handler_backends
from telebot import types

from hiddify_support_bot.basebot.custom_message_types import HMessage
from .data_storage import DataStorage
from .roles import Role
from hiddify_support_bot.utils import start_param


class Middleware(asyncio_handler_backends.BaseMiddleware):
    def __init__(self, bot):
        self.bot = bot
        self.update_types = [
            "message",
            "edited_message",
            "channel_post",
            "edited_channel_post",
            "inline_query",
            "chosen_inline_result",
            "callback_query",
            "shipping_query",
            "pre_checkout_query",
            "poll",
            "poll_answer",
            "my_chat_member",
            "chat_member",
            "chat_join_request",
            "message_reaction",
            "message_reaction_count",
            "chat_boost",
            "removed_chat_boost",
            "business_connection",
            "business_message",
            "edited_business_message",
            "deleted_business_messages",
        ]

    async def set_basic_elements(self, obj, data):
        # print(obj)
        user_id = chat_id = deflang = None
        base = obj
        if isinstance(obj, types.CallbackQuery):
            if not obj.message:
                return
            base = obj.message

            chat_id = base.chat.id
            user_id = obj.from_user.id
            deflang = base.from_user.language_code
        elif isinstance(obj, types.InlineQuery):
            user_id = obj.from_user.id
            deflang = obj.from_user.language_code
            base = obj
        else:
            base = obj

            chat_id = base.chat.id
            user_id = base.from_user.id if base.from_user else None
            deflang = base.from_user.language_code if base.from_user else "fa"

        if isinstance(base, types.Message):
            reply_msg = base
            while reply_msg:
                reply_msg.text = getattr(reply_msg, "caption") or getattr(reply_msg, "text") or ""
                reply_msg.entities = getattr(reply_msg, "caption_entities") or getattr(reply_msg, "entities") or []
                base.main_message = reply_msg
                reply_msg = reply_msg.reply_to_message
        base.chat_id = chat_id
        base.user_id = user_id
        # data['lang']="en"
        base.db = db = DataStorage(self.bot, user_id, chat_id)
        base.common_db = DataStorage(self.bot, 0, 0)
        if hasattr(base, "text") and base.text and base.text.startswith("/start"):
            action, params = start_param.decode(base.text)
            data['start_action'] = action
            data['start_params'] = params
            deflang = params.get("lang", deflang)
            await db.set("lang", deflang)
        lang = await db["lang"]
        if not lang:
            await db.set("lang", deflang)
            lang = deflang
        base.lang = lang
        base.role = await db["role"]

        return base

    def get_role(self): pass

    async def set_user_data(self, base: HMessage, data):
        db = base.db
        if isinstance(base, types.Message) and data.get('start_action'):

            try:

                # if len(params)>1:
                #     invite_links=await base.common_db.get("invite_links",{})
                #     if invite_links.get(params[1],{}).get("admin"):
                #         await db.set(role = Role.SUPER_ADMIN)
                #     elif invite_links.get(params[1],{}).get("support"):
                #         await db.set(role = Role.SUPPORT)
                await db.set(role=Role.USER)
            except Exception as e:
                logger.error(e)

                await db.set(role=Role.UNKNOWN)

    async def pre_process(self, obj, data):
        base = await self.set_basic_elements(obj, data)
        if not base:
            return
        await self.set_user_data(base, data)

        if isinstance(obj, types.Message):
            if base.chat_id:
                await self.bot.send_chat_action(base.chat_id, "typing")
            # from hiddify_support_bot.utils import tghelper
            # await tghelper.set_reaction(base)

    async def post_process(self, message, data, exception):
        pass

    # Update other methods in Middleware to be async as well
