from fastapi.responses import StreamingResponse
import aiohttp
from JioSaavn import search


async def get_stream_url(query: str):
    results = await search(query, limit=1)

    if not results:
        return None, None

    song = results[0]

    return song.get("media_url"), song


async def stream_audio(query: str):
    stream_url, song = await get_stream_url(query)

    if not stream_url:
        return {"error": "Song not found"}

    session = aiohttp.ClientSession()

    async def generator():
        async with session.get(stream_url) as resp:
            async for chunk in resp.content.iter_chunked(1024):
                yield chunk
        await session.close()

    return StreamingResponse(
        generator(),
        media_type="audio/mpeg",
        headers={
            "X-Title": song.get("song"),
            "X-Artist": song.get("primary_artists")
        }
    )
