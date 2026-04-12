import aiohttp
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse

from JioSaavn import search

app = FastAPI()

# 🔥 LOGGER SETUP
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

LOGGER = logging.getLogger("SaavnAPI")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home():
    return FileResponse("static/index.html")


# 🔍 SEARCH
@app.post("/api/search")
async def search_api(req: Request):
    try:
        data = await req.json()
        q = data.get("q")

        if not q:
            return JSONResponse(
                status_code=400,
                content={"error": "Query is required"}
            )

        LOGGER.info(f"Search query: {q}")

        results = await search(q, limit=10)

        if not results:
            LOGGER.warning(f"No results for: {q}")
            return []

        return [
            {
                "title": s.get("song"),
                "url": s.get("media_url"),
                "thumbnail": s.get("image"),
                "channel": s.get("primary_artists"),
                "duration": s.get("duration", "3:00")
            }
            for s in results if s.get("media_url")
        ]

    except Exception as e:
        LOGGER.exception(f"Search error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Search failed"}
        )


# 🎵 AUDIO STREAM
@app.post("/api/play/audio")
async def play_audio(req: Request):
    try:
        data = await req.json()
        url = data.get("url")

        if not url:
            return JSONResponse(
                status_code=400,
                content={"error": "No URL provided"}
            )

        LOGGER.info(f"Streaming URL: {url}")

        session = aiohttp.ClientSession()

        async def generator():
            try:
                async with session.get(url) as resp:

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
            media_type="audio/mpeg"
        )

    except Exception as e:
        LOGGER.exception(f"Play audio error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Streaming failed"}
        )


# ❌ VIDEO NOT SUPPORTED
@app.get("/api/play/video")
async def play_video():
    return JSONResponse(
        status_code=400,
        content={"error": "Video not supported "}
    )
