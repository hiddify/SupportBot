from telebot import asyncio_filters,types
from .storage_filter import StorageFilter
from . import Role
class RoleFilter(StorageFilter):

    key = 'role'

    async def check(self, obj, val):
        data={Role.USER}
        if val==Role.SUPER_ADMIN:
            data={Role.SUPER_ADMIN}
        elif val==Role.SUPPORT:
            data={Role.SUPPORT,Role.SUPER_ADMIN}
        # elif val==Role.AGENT:
        #     data={Role.SUPER_ADMIN,Role.ADMIN,Role.AGENT}
        return await super().check(obj,{"role":data})
            
        
