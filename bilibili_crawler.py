import requests
from bs4 import BeautifulSoup as BS
import json
from typing import List, Dict
import re
import subprocess
import logging
import os
import argparse


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


def get_user_all_video_info(uid: str, headers, download_addr: str, tid: int = 0) -> None:
    """
    Get the video info of some bilibili user whose id is `uid`.

    Args:
        uid: The id of the user.
        tid: The type id of the video. 0 means all types.
    """
    page = 1
    url_prefix = f"https://api.bilibili.com/x/space/wbi/arc/search?mid={uid}&ps=50&tid={tid}&pn="
    post_video_list = []
    logging.info(f"Start Collecting {uid}'s video info.")
    while True:
        try:
            resp = requests.get(url=url_prefix + str(page),
                                headers=headers).json()
            assert resp["code"] == 0
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                logging.warning(
                    "Keyboard interrupt detected. The program will exit.")
                return
            else:
                logging.error(
                    f"Failed to get {uid}'s video info. You may need to check your network or update your cookie.")
            return
        if resp["data"]["list"]["vlist"] == []:
            break
        else:
            for item in resp["data"]["list"]["vlist"]:
                info = {}
                info["title"] = item["title"]
                info["bvid"] = item["bvid"]
                post_video_list.append(info)
            page += 1
    if page == 1:
        logging.warning(f"User {uid} has no video.")
    logging.info(f"Finished Collecting {uid}'s video info.")
    with open(download_addr + "video_list.json", "w", encoding="utf-8") as f:
        json.dump(post_video_list, f)


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


def add_url_to_set(url_set: set, url_list: List) -> None:
    for url in url_list:
        if isinstance(url, list):
            for item in url:
                url_set.add(item)
        else:
            url_set.add(url)

def get_all_video_audio_url(bvid: str, headers, quality_v: str, quality_a: str) -> Dict:
    """
    Get all the video and audio download url of a post whose bvid is `bvid`.

    Args:
        bvid: The bvid of the post video.
        headers: The headers of requests.
        quality_v: The quality of video.
        quality_a: The quality of audio.

    Returns:
        info: A dict of video, audio download url and title.
    """
    url = f'https://www.bilibili.com/video/{bvid}/'  # the last slash is necessary !!!
    response = requests.get(url, headers=headers).text
    soup = BS(response, "lxml")
    player_info_str = (soup.find_all("script")[2].text)[20:]
    player_info = json.loads(player_info_str)
    info = dict()
    info["title"] = re.findall(
        '<title data-vue-meta="true">(.*?)_', response)[0]
    video_id, audio_id = get_quality_id(quality_v, quality_a)
    info["video_url"], info["audio_url"] = set(), set()
    for item in player_info["data"]["dash"]["video"]:
        if item["id"] == video_id:
            add_url_to_set(info["video_url"], [item["baseUrl"], item["base_url"],
                                               item["backupUrl"], item["backup_url"]])
    for item in player_info["data"]["dash"]["audio"]:
        if item["id"] == audio_id:
            add_url_to_set(info["audio_url"], [item["baseUrl"], item["base_url"],
                                               item["backupUrl"], item["backup_url"]])
    info["video_url"].discard(None), info["audio_url"].discard(None)
    return info



def get_video_audio_url(bvid: str, headers, quality_v: str, quality_a: str) -> Dict:
    """
    Get the video and audio download url of a post whose bvid is `bvid`.

    Args:
        bvid: The bvid of the post video.
        headers: The headers of requests.
        quality_v: The quality of video.
        quality_a: The quality of audio.

    Returns:
        info: A dict of video, audio download url and title.
    """
    url = f'https://www.bilibili.com/video/{bvid}/'  # the last slash is necessary !!!
    response = requests.get(url, headers=headers).text
    soup = BS(response, "lxml")
    player_info_str = (soup.find_all("script")[2].text)[20:]
    player_info = json.loads(player_info_str)
    info = dict()
    info["title"] = re.findall(
        '<title data-vue-meta="true">(.*?)_', response)[0]
    video_id, audio_id = get_quality_id(quality_v, quality_a)
    for item in player_info["data"]["dash"]["video"]:
        if item["id"] == video_id:
            info["video_url"] = item["baseUrl"]
            break
    for item in player_info["data"]["dash"]["audio"]:
        if item["id"] == audio_id:
            info["audio_url"] = item["baseUrl"]
            break
    return info


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


def re_find_download_file(bvid: str, headers, quality_v: str, quality_a: str, download_addr: str) -> bool:
    """
    Try to find the all the download url of a given `bvid`, and download a right version.

    Returns:
        True if the download is successful, otherwise False.
    """
    logging.info(f"Retry downloading {bvid}.")
    info = get_all_video_audio_url(bvid, headers, quality_v, quality_a)
    for item in info["video_url"]:
        try:
            download_file(item, info["title"], "video", headers, download_addr)
        except:
            continue
        else:
            break
    for item in info["audio_url"]:
        try:
            download_file(item, info["title"], "audio", headers, download_addr)
        except:
            continue
        else:
            break
    if not os.path.exists(download_addr + info["title"] + "_video.m4s") or not os.path.exists(download_addr + info["title"] + "_audio.m4s"):
        logging.warning(f"Failed to download {bvid}.")
        return False
    mix_video_audio(info["title"] + "_video.m4s", info["title"] +
                    "_audio.m4s", info["title"] + ".mp4", download_addr)
    return True


def crawl_bv_list(bvid_list: List,
                  headers,
                  begin: int,
                  download_addr: str,
                  quality_v: str,
                  quality_a: str) -> List:
    """
    Crawl the video and audio of the post whose bvid is `bvid`.

    Args:
        bvid_list: The list of bvid.
        headers: The headers of requests.
        begin: The begin index (from zero) of bvid_list.
        download_addr: The root address of download files.
        quality_v: The quality of video.
        quality_a: The quality of audio.

    Returns:
        unsuccessful_list: The list of bvid index (from zero) which failed to download.
    """
    if not os.path.exists(download_addr):
        os.mkdir(download_addr)

    total_websites = len(bvid_list)
    if begin >= total_websites:
        logging.warning("Begin index out of range.")
        return []
    logging.info(f"Total number of sites crawled: {total_websites}.")
    bvid_list = bvid_list[begin:]
    unsuccessful_list = []
    for index, bvid in enumerate(bvid_list, start=1+begin):
        try:
            info = get_video_audio_url(bvid, headers, quality_v, quality_a)
            logging.info(
                f'Crawling {index}/{total_websites} - {info["title"]}.')
            download_file(info["video_url"], info["title"],
                          "video", headers, download_addr)
            download_file(info["audio_url"], info["title"],
                          "audio", headers, download_addr)
            mix_video_audio(info["title"] + "_video.m4s",
                            info["title"] + "_audio.m4s",
                            info["title"] + ".mp4",
                            download_addr)
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                logging.error(
                    "Keyboard interrupt detected. The program will exit.")
                return unsuccessful_list
            else:
                logging.warning(f'{str(e)}')
                try:
                    if re_find_download_file(bvid, headers, quality_v, quality_a, download_addr):
                        logging.info(
                            f'Finished {index}/{total_websites} - {info["title"]}.')
                    else:
                        logging.warning(
                            f"Failed to crawl {index}/{total_websites} - {info['title']}. You may need to check your network or update your cookie.")
                        unsuccessful_list.append(index - 1)
                except:
                    logging.warning(
                        f"Failed to crawl {index}/{total_websites} - {info['title']}. You may need to check your network or update your cookie.")
                    unsuccessful_list.append(index - 1)
            continue
        else:
            logging.info(
                f'Finished {index}/{total_websites} - {info["title"]}.')
    if len(unsuccessful_list) > 0:
        logging.warning(
            f"Failed to crawl {len(unsuccessful_list)}/{total_websites} video(s).")
        logging.warning(f"Unsuccessful list: {unsuccessful_list}")
    else:
        logging.info(f"All {total_websites} video(s) have been downloaded!")
    return unsuccessful_list


def crawl_user_all_video(uid: str,
                         headers,
                         download_addr: str = "./download/",
                         quality_v: str = "720p",
                         quality_a: str = "132k") -> None:
    """
    Crawl all videos of the user whose uid is `uid`.

    Args:
        uid: The uid of the user.
        headers: The headers of requests.
        download_addr: The root address of download files.
        quality_v: The quality of video.
        quality_a: The quality of audio.
    """
    download_addr = download_addr + uid + "/"
    if not os.path.exists(download_addr):
        os.mkdir(download_addr)
    get_user_all_video_info(uid, headers, download_addr=download_addr)
    if not os.path.exists(download_addr + "video_list.json"):
        logging.error("No video list found!")
        return
    with open(download_addr + "video_list.json", "r", encoding="utf-8") as f:
        video_list = json.load(f)
    bv_list = [item["bvid"] for item in video_list]
    crawl_bv_list(bv_list, headers, 0, download_addr, quality_v, quality_a)


def parse_arguments() -> argparse.Namespace:
    """
    Parse the arguments.
    """
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-u", "--uid", type=str,
                       required=False, help="The uid of the user.")
    group.add_argument("-b", "--bvid", type=str, required=False,
                       help="The bvid of the video.")
    parser.add_argument("-v", "--quality_v", type=str,
                        default="720p", help="The quality of video. The options are 1080p, 720p, 480p, 360p.")
    parser.add_argument("-a", "--quality_a", type=str,
                        default="132k", help="The quality of audio. The options are 64k, 132k, 192k.")
    parser.add_argument("-d", "--download_addr", type=str, default="./download/",
                        help="The root address of download files.")
    args = parser.parse_args()
    if args.download_addr[-1] != "/":
        args.download_addr += "/"
    return args


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    headers = set_headers()
    args = parse_arguments()
    if args.uid:
        crawl_user_all_video(args.uid, headers, args.download_addr,
                             args.quality_v, args.quality_a)
    elif args.bvid:
        crawl_bv_list([args.bvid], headers, 0, args.download_addr,
                      args.quality_v, args.quality_a)
    else:
        logging.error("Please specify the uid or bvid!")
