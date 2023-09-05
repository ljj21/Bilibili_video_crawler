import logging
import re
import requests
import subprocess
import os
import json
from typing import Dict

def get_quality_id(quality_v: str, quality_a: str) -> (int, int):
    """
    Get the quality id of video and audio.

    Args:
        quality_v: The quality of video.
        quality_a: The quality of audio.

    Returns:
        video_id: The id of video.
        audio_id: The id of audio.
    """
    video_d = {
        "1080p": 80,
        "720p": 64,
        "480p": 32,
        "360p": 16,
    }
    audio_d = {
        "64k": 30216,
        "132k": 30232,
        "192k": 30280,
    }
    return video_d[quality_v] if quality_v in video_d else 64, \
        audio_d[quality_a] if quality_a in audio_d else 30232

def get_quality_str(quality_v: str, quality_a: str) -> (str, str):
    """
    Get the quality id of video and audio.

    Args:
        quality_v: The quality of video.
        quality_a: The quality of audio.

    Returns:
        video_id: The id of video.
        audio_id: The id of audio.
    """
    video_d = {
        "1080p": "100026",
        "720p": "100024",
        "480p": "100023",
        "360p": "100022",
    }
    audio_d = {
        "64k": "30216",
        "132k": "30232",
        "192k": "30280",
    }
    return video_d[quality_v] if quality_v in video_d else "100024", \
        audio_d[quality_a] if quality_a in audio_d else "30232"


def set_headers() -> Dict:
    """
    Set headers for requests.

    Returns:
        headers: A dict of headers.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/"
    }
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    headers["cookie"] = config["cookie"]
    return headers


def download_file(url: str, title: str, suffix: str, headers, download_addr: str) -> None:
    """
    Download the file from url.

    Args:
        url: The download url of the file.
        title: The title of the post.
        suffix: The suffix of the saved file. Options: ["video", "audio"]
    """
    file_name = title + "_" + suffix + ".m4s"
    r = requests.get(url, stream=True, headers=headers)
    logging.info(f"Downloading {suffix} file: {file_name}.")
    # file name cannot contain the following characters: \ / : * ? " < > |
    file_name_modified = re.sub(r'[\\/:*?"<>|]', ' ', file_name)
    with open(download_addr + file_name_modified, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)

    logging.info(f"{file_name} downloaded!")


def mix_video_audio(input_video: str, input_audio: str, output_file: str, download_addr: str) -> None:
    """
    Mix the video and the corresponding audio.
    """
    # file name cannot contain the following characters: \ / : * ? " < > |
    input_video = re.sub(r'[\\/:*?"<>|]', ' ', input_video)
    input_audio = re.sub(r'[\\/:*?"<>|]', ' ', input_audio)
    output_file = re.sub(r'[\\/:*?"<>|]', ' ', output_file)
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", download_addr + input_video,
        "-i", download_addr + input_audio,
        "-c:v", "copy",
        "-c:a", "copy",
        download_addr + output_file
    ]
    subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    logging.info("Video and audio have been mixed!")
    os.remove(download_addr + input_video)
    os.remove(download_addr + input_audio)


def download_and_mix(info: Dict,
                     headers,
                     download_addr: str) -> None:
    logging.info(
        f'The title of this video is - {info["title"]}.')
    download_file(info["video_url"], info["title"],
                  "video", headers, download_addr)
    download_file(info["audio_url"], info["title"],
                  "audio", headers, download_addr)
    mix_video_audio(info["title"] + "_video.m4s",
                    info["title"] + "_audio.m4s",
                    info["title"] + ".mp4",
                    download_addr)