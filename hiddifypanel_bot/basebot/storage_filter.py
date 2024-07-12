from telebot import asyncio_filters,types
from . import bot
class StorageFilter(asyncio_filters.AdvancedCustomFilter):

    key = 'db'

    async def check(self, obj, val):
        """
        :meta private:
        """
        if isinstance(obj,types.Message):
            message=obj
        elif hasattr(obj,'message'):
            message=obj.message
        else:
            return 
        if not isinstance(val, dict):
            raise ValueError("Invalid Usage")
        
        storage=message.db
        for k,v in val.items():    
            l=v if isinstance(v, list) else [v]
            data=await storage[k]
            for filter in l:
                if isinstance(filter,asyncio_filters.SimpleCustomFilter): 
                    if filter.check(data):
                        return True
                else:
                    if isinstance(filter,list) or isinstance(filter,set):
                        return data in filter
                    else:
                        return data==filter
        return False

