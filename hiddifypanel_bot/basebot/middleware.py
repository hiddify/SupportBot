from asyncio.log import logger
import os
from telebot import asyncio_handler_backends
from telebot import types
from .data_storage import DataStorage
from .roles import Role
from hiddifypanel_bot.hiddifyapi import HiddifyApi

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
            user_id = base.from_user.id
            deflang = base.from_user.language_code
        base.chat_id = chat_id
        base.user_id = user_id
        # data['lang']="en"
        base.db = db = DataStorage(self.bot, user_id, chat_id)
        if not await db.get_state():await db.set_state("init")
        lang = await db["lang"]
        if not lang:
            await db.set("lang", deflang)
            lang =deflang
        base.lang = lang
        base.role = await db["role"]
        base.hapi = HiddifyApi(await base.db["guid"])
        return base

    async def set_user_data(self, base):
        db = base.db
        if isinstance(base, types.Message) and base.text and base.text.startswith("/start"):
            params = base.text.split()
            try:
                if len(params) >= 2 and "admin" in params[1]:
                    uid = params[1].split("_")[1]
                    hapi = HiddifyApi(uid)
                    info=hapi.get_admin_info()
                    role = info["mode"]
                    if role == "super_admin":
                        role = Role.SUPER_ADMIN
                    if role == "admin":
                        role = Role.ADMIN
                    if role == "agent":
                        role = Role.AGENT

                    await db.set(info = info,
                                 guid=uid,
                                 admin_link = hapi.get_admin_link(),
                                 role=role)
                    
                
                elif len(params) >= 2:
                    uid = params[1]
                    base.hapi = HiddifyApi(uid)
                    await db.set(
                        info = base.hapi.get_user_info(),
                        guid = uid,
                        role=Role.USER)
                    base.role =  Role.USER
            except Exception as e:
                logger.error(e)

                await db.set(role = Role.UNKNOWN,guid="")
            
            base.hapi = HiddifyApi(await base.db["guid"])
            

    async def pre_process(self, obj, data):
        base = await self.set_basic_elements(obj, data)
        if not base:
            return
        await self.set_user_data(base)

        if base.chat_id:
            await self.bot.send_chat_action(base.chat_id, "typing")
        if isinstance(obj, types.Message):
            from hiddifypanel_bot.utils import tghelper

            await tghelper.set_reaction(base)

    async def post_process(self, message, data, exception):
        pass

    # Update other methods in Middleware to be async as well
