from redis import asyncio as aioredis
from python_app1.settings import settings


KEY = "SUPER-KEY"


class RedisRepo:

    def __init__(self):
        self.conn = aioredis.from_url(f"redis://{settings.redis_host}:{settings.redis_port}", decode_responses=True)

    async def set_val(self, value):
        await self.conn.set(KEY, value)
        return True
    
    async def get_value(self):
        return await self.conn.get(KEY)
    
    async def delete_value(self):
        await self.conn.delete(KEY)
        return True
