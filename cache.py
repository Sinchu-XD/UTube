cache = {}

async def init():
    pass

async def get(key):
    return cache.get(key)

async def set(key, value):
    cache[key] = value
