import subprocess
from fastapi.responses import StreamingResponse


def get_video_audio_urls(url: str):

    cmd = [
        "yt-dlp",
        "--cookies", "cookies.txt",
        "--js-runtimes", "node",
        "--remote-components", "ejs:github",
        "--extractor-args", "youtube:player_js_variant=main",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]",
        "--no-playlist",
        "-g",
        url
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(result.stderr)
        return None, None

    urls = result.stdout.strip().split("\n")

    if len(urls) < 2:
        return None, None

    return urls[0], urls[1]


import asyncio
import os
import uuid

HLS_DIR = "hls"

os.makedirs(HLS_DIR, exist_ok=True)


async def run_cmd(cmd):
    process = await asyncio.create_subprocess_exec(*cmd)
    await process.communicate()


async def generate_hls(video_url, audio_url):

    stream_id = str(uuid.uuid4())
    out_path = f"{HLS_DIR}/{stream_id}.m3u8"

    cmd = [
        "ffmpeg",
        "-i", video_url,
        "-i", audio_url,
        "-c:v", "copy",
        "-c:a", "aac",
        "-f", "hls",
        "-hls_time", "6",
        "-hls_list_size", "0",
        "-hls_segment_filename", f"{HLS_DIR}/{stream_id}_%03d.ts",
        out_path
    ]

    await run_cmd(cmd)

    return stream_id
