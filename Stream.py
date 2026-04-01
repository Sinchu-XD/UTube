import asyncio
import subprocess
import os
import uuid

HLS_DIR = "hls"
COOKIES = "cookies.txt"

os.makedirs(HLS_DIR, exist_ok=True)


def get_cookie_file():
    return COOKIES if os.path.exists(COOKIES) else None


async def run_blocking(cmd):
    return await asyncio.to_thread(
        subprocess.run,
        cmd,
        capture_output=True,
        text=True
    )


async def get_video_audio_urls(url: str, cookies=None):

    cmd = [
        "yt-dlp",
        "--js-runtimes", "node",
        "--remote-components", "ejs:github",
        "--extractor-args", "youtube:player_js_variant=main",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]",
        "--no-playlist",
        "-g",
        url
    ]

    cookies = get_cookie_file()
    if cookies:
        cmd.insert(1, "--cookies")
        cmd.insert(2, cookies)

    result = await run_blocking(cmd)

    if result.returncode != 0:
        print(result.stderr)
        return None, None

    urls = result.stdout.strip().split("\n")

    if len(urls) < 2:
        return None, None

    return urls[0], urls[1]


async def generate_hls(video_url: str, audio_url: str):

    stream_id = str(uuid.uuid4())
    output_path = f"{HLS_DIR}/{stream_id}.m3u8"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_url,
        "-i", audio_url,
        "-c:v", "copy",
        "-c:a", "aac",
        "-f", "hls",
        "-hls_time", "6",
        "-hls_list_size", "0",
        "-hls_segment_filename", f"{HLS_DIR}/{stream_id}_%03d.ts",
        output_path
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )

    await process.wait()

    return stream_id


def cleanup_hls(max_age=3600):
    now = asyncio.get_event_loop().time()

    for file in os.listdir(HLS_DIR):
        path = os.path.join(HLS_DIR, file)

        if os.path.isfile(path):
            if os.stat(path).st_mtime < (now - max_age):
                try:
                    os.remove(path)
                except:
                    pass
