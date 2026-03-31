import redis.asyncio as redis
import json

r = None

async def init():
    global r
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)

async def get(key):
    data = await r.get(key)
    return json.loads(data) if data else None

async def set(key, value):
    await r.set(key, json.dumps(value), ex=3600)
