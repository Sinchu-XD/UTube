from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from YouTubeMusic.Search import Search
from YouTubeMusic.Stream import get_stream
from Stream import get_video_audio_urls, stream_merged

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


# 🔍 SEARCH
@app.post("/api/search")
async def search(req: Request):
    data = await req.json()
    return await Search(data.get("q"), limit=1)


# 📁 COOKIE PATH
COOKIES = "cookies.txt"

def get_cookie_file():
    return COOKIES if os.path.exists(COOKIES) else None


@app.post("/api/play/audio")
async def play_audio(req: Request):
    data = await req.json()
    url = data.get("url")

    stream = await get_stream(url, cookies=get_cookie_file())

    if not stream:
        return {"error": "Audio stream failed"}

    return {"stream": stream}


@app.get("/api/play/video")
async def play_video(url: str):

    video_url, audio_url = get_video_audio_urls(url)

    if not video_url or not audio_url:
        return {"error": "Video stream failed"}

    return stream_merged(video_url, audio_url)
