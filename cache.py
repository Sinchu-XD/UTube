import aioredis
import json

redis = None

async def init():
    global redis
    redis = await aioredis.from_url("redis://localhost", decode_responses=True)

async def get(key):
    data = await redis.get(key)
    return json.loads(data) if data else None

async def set(key, value):
    await redis.set(key, json.dumps(value), ex=3600)
