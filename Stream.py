import aiohttp
import logging

from fastapi.responses import StreamingResponse, JSONResponse
from JioSaavn import search


# 🔥 LOGGER SETUP
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

LOGGER = logging.getLogger("SaavnAPI")


async def get_stream_url(query: str):
    try:
        results = await search(query, limit=1)

        if not results:
            LOGGER.warning(f"No results found for query: {query}")
            return None, None

        song = results[0]
        url = song.get("media_url")

        if not url:
            LOGGER.error(f"No media_url found for song: {song}")
            return None, None

        return url, song

    except Exception as e:
        LOGGER.exception(f"Search error for query '{query}': {e}")
        return None, None


async def stream_audio(query: str):
    try:
        stream_url, song = await get_stream_url(query)

        if not stream_url:
            return JSONResponse(
                status_code=404,
                content={"error": "Song not found"}
            )

        session = aiohttp.ClientSession()

        async def generator():
            try:
                async with session.get(stream_url) as resp:

                    if resp.status != 200:
                        LOGGER.error(f"Stream failed: {resp.status}")
                        yield b""
                        return

                    async for chunk in resp.content.iter_chunked(1024):
                        yield chunk

            except Exception as e:
                LOGGER.exception(f"Streaming error: {e}")
                yield b""

            finally:
                await session.close()

        return StreamingResponse(
            generator(),
            media_type="audio/mpeg",
            headers={
                "X-Title": song.get("song", "Unknown"),
                "X-Artist": song.get("primary_artists", "Unknown")
            }
        )

    except Exception as e:
        LOGGER.exception(f"Fatal stream error: {e}")

        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error"}
        )
