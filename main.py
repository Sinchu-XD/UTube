from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import os

from cache import init, get, set
from Stream import get_video_audio_urls, generate_hls
from YouTubeMusic.Search import Search
from YouTubeMusic.Stream import get_stream

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/hls", StaticFiles(directory="hls"), name="hls")

COOKIES = "cookies.txt"


def get_cookie_file():
    return COOKIES if os.path.exists(COOKIES) else None


@app.on_event("startup")
async def startup():
    await init()


@app.get("/")
async def home():
    return FileResponse("static/index.html")


@app.post("/api/search")
async def search(req: Request):
    data = await req.json()
    return await Search(data.get("q"), limit=5)


@app.post("/api/play/audio")
async def play_audio(req: Request):
    data = await req.json()
    url = data.get("url")

    cache_key = f"audio:{url}"

    cached = await get(cache_key)
    if cached:
        return {"stream": cached}

    stream = await get_stream(url, cookies=get_cookie_file())

    if not stream:
        return {"error": "audio failed"}

    await set(cache_key, stream)

    return {"stream": stream}


@app.get("/api/play/video")
async def play_video(url: str):

    cache_key = f"hls:{url}"

    cached = await get(cache_key)
    if cached:
        return {"stream": f"/hls/{cached}.m3u8"}

    video_url, audio_url = await get_video_audio_urls(
        url,
        get_cookie_file()
    )

    if not video_url:
        return {"error": "video failed"}

    stream_id = await generate_hls(video_url, audio_url)

    await set(cache_key, stream_id)

    return {"stream": f"/hls/{stream_id}.m3u8"}
