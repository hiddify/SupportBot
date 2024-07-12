from telebot import asyncio_filters,types
class CallActionFilter(asyncio_filters.AdvancedCustomFilter):
    

    key = 'call_action'

    async def check(self, obj, val):
        if not isinstance(obj,types.CallbackQuery):
            return
        if not obj.data:return
        action= obj.data.split(":")[0]
        if isinstance(val ,list) or isinstance(val ,set):
            return action in val
        return action==val

