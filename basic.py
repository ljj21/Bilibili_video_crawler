import logging
import re
import requests
import subprocess
import os

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