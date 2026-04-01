import subprocess
from fastapi.responses import StreamingResponse


def get_video_audio_urls(url: str, quality="auto"):

    formats = {
        "360": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]",
        "480": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]",
        "720": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]",
        "1080": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]",
        "1440": "bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]",
        "2160": "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]"
    }

    if quality == "auto":
        fmt = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]"
    else:
        fmt = formats.get(quality, formats["720"])

    cmd = [
        "yt-dlp",
        "--cookies", "cookies.txt",
        "--js-runtimes", "node",
        "--remote-components", "ejs:github",
        "--extractor-args", "youtube:player_js_variant=main",
        "-f", fmt,
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


def stream_merged(video_url: str, audio_url: str):

    ffmpeg_cmd = [
        "ffmpeg",
        "-i", video_url,
        "-i", audio_url,
        "-c:v", "copy",
        "-c:a", "copy",
        "-f", "mp4",
        "-movflags", "frag_keyframe+empty_moov",
        "pipe:1"
    ]

    process = subprocess.Popen(
        ffmpeg_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )

    return StreamingResponse(
        process.stdout,
        media_type="video/mp4"
    )
