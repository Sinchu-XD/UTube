from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import aiohttp

from JioSaavn import search

app = FastAPI()

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


# 🔍 SEARCH (JioSaavn)
@app.post("/api/search")
async def search_api(req: Request):
    data = await req.json()
    q = data.get("q")

    results = await search(q, limit=10)

    return [
        {
            "title": s.get("song"),
            "url": s.get("media_url"),
            "thumbnail": s.get("image"),
            "channel": s.get("primary_artists"),
            "duration": s.get("duration", "3:00")
        }
        for s in results
    ]


# 🎵 AUDIO STREAM (JioSaavn)
@app.post("/api/play/audio")
async def play_audio(req: Request):
    data = await req.json()
    url = data.get("url")

    if not url:
        return {"error": "No URL provided"}

    session = aiohttp.ClientSession()

    async def generator():
        async with session.get(url) as resp:
            async for chunk in resp.content.iter_chunked(1024):
                yield chunk
        await session.close()

    return StreamingResponse(
        generator(),
        media_type="audio/mpeg"
    )


# ❌ VIDEO NOT SUPPORTED (JioSaavn audio only)
@app.get("/api/play/video")
async def play_video():
    return {"error": "Video not supported soon we will"}
