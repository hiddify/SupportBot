from telebot import asyncio_filters, types


class StepFilter(asyncio_filters.AdvancedCustomFilter):
    def __init__(self, bot):
        self.bot = bot

    key = "step"

    async def check(self, message, text):
        """
        :meta private:
        """
        if isinstance(message, types.Message) and message.text and message.text.startswith("/"):
            return False

        # needs to work with callbackquery
        if isinstance(message, types.Message):
            chat_id = message.chat.id
            user_id = message.from_user.id
        elif isinstance(message, types.CallbackQuery):

            chat_id = message.message.chat.id
            user_id = message.from_user.id
            message = message.message
        else:
            return False

        return await message.db.get("__step__") == text
