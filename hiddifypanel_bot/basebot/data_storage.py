
class DataStorage:
    def __init__(self, bot, user_id, chat_id):
        self.user_id = user_id
        self.chat_id = chat_id
        self.bot=bot
        

    async def get_state(self) -> str:
        return await self.bot.get_state(self.user_id, self.chat_id)

    async def set_state(self, state: str):
        await self.bot.set_state(self.user_id, state, self.chat_id)

    async def __getitem__(self, key,defv=None):
        async with self.bot.retrieve_data(self.user_id, self.chat_id) as storage:
            if not storage:
                return defv
            return storage.get(key,defv)

    async def all(self):
        async with self.bot.retrieve_data(self.user_id, self.chat_id) as storage:
            return storage

    async def get(self, key,defv=None):
        return self.__getitem__(key,defv)
    
    async def __setitem__(self, key, value):
        await self.bot.add_data(self.user_id, self.chat_id, **{key: value})

    async def set(self, k=None, v=None,**kwargs):
        if k is not None:
            kwargs[k]=v
        await self.bot.add_data(self.user_id, self.chat_id, **kwargs)