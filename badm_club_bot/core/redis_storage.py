from redis.asyncio import Redis
from aiogram.fsm.storage.redis import RedisStorage

def create_redis_storage():
    redis = Redis(
        host="redis",
        port=6379,
        db=0
    )
    return RedisStorage(redis=redis)