import requests
from bs4 import BeautifulSoup as BS
import json
from typing import List, Dict
import re
import logging
import os

from basic import download_and_mix, get_quality_id

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
        resp = requests.get(url=url_prefix + str(page),
                            headers=headers).json()
        assert resp["code"] == 0
        if resp["data"]["list"]["vlist"] == []:
            break
        else:
            for item in resp["data"]["list"]["vlist"]:
                info = {}
                info["title"] = item["title"]
                info["id"] = item["bvid"]
                post_video_list.append(info)
            page += 1
    if page == 1:
        logging.warning(f"User {uid} has no video.")
    logging.info(f"Finished Collecting {uid}'s video info.")
    with open(download_addr + "video_list.json", "w", encoding="utf-8") as f:
        json.dump(post_video_list, f)


def get_download_url(bvid: str, headers, quality_v: str, quality_a: str) -> Dict:
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
    for item in player_info["data"]["dash"]["video"]:
        if item["id"] == quality_v:
            info["video_url"] = item["baseUrl"]
    for item in player_info["data"]["dash"]["audio"]:
        if item["id"] == quality_a:
            info["audio_url"] = item["baseUrl"]
    return info


def get_download_url(bvid: str, headers, quality_v: str, quality_a: str) -> Dict:
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
    for item in player_info["data"]["dash"]["video"]:
        if item["id"] == quality_v:
            info["video_url"] = item["baseUrl"]
            break
    for item in player_info["data"]["dash"]["audio"]:
        if item["id"] == quality_a:
            info["audio_url"] = item["baseUrl"]
            break
    return info


def crawl_user_all_video(uid: str,
                         headers,
                         download_addr: str,
                         quality_v: str,
                         quality_a: str) -> None:
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
        os.makedirs(download_addr)
    try:
        get_user_all_video_info(uid, headers, download_addr=download_addr)
    except Exception as e:
        if isinstance(e, KeyboardInterrupt):
            logging.warning(
                "Keyboard interrupt detected. The program will exit.")
        else:
            logging.error(
                f"Failed to get {uid}'s video info. You may need to check your network or update your cookie.")
        return
    if not os.path.exists(download_addr + "video_list.json"):
        logging.error("No video list found!")
        return
    with open(download_addr + "video_list.json", "r", encoding="utf-8") as f:
        video_list = json.load(f)
    bv_list = [item["id"] for item in video_list]  # bvid
    crawl_bv_list(bv_list, headers, download_addr, quality_v, quality_a)


def crawl_bv_list(bvid_list: List[str],
                  headers,
                  download_addr: str,
                  quality_v: str,
                  quality_a: str) -> None:
    total_websites = len(bvid_list)
    if total_websites == 0:
        logging.warning("There is no video to crawl.")
        return
    logging.info(f"Total number of sites crawled: {total_websites}.")
    unsuccessful_list = []
    quality_v, quality_a = get_quality_id(quality_v, quality_a)
    for index, bvid in enumerate(bvid_list, start=1):
        logging.info(
            f'Crawling {index}/{total_websites}.')
        try:
            info = get_download_url(bvid, headers, quality_v, quality_a)
            download_and_mix(info, headers, download_addr)
            logging.info(
                f'Finished {index}/{total_websites}.')
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                logging.error(
                    "Keyboard interrupt detected. The program will exit.")
                return
            else:
                logging.warning(
                    f"Failed to crawl {index}/{total_websites}. You may need to check your network or update your cookie.")
                unsuccessful_list.append(index - 1)
    if len(unsuccessful_list) > 0:
        logging.warning(
            f"Failed to crawl {len(unsuccessful_list)}/{total_websites} video(s).")
        logging.warning(f"Unsuccessful list: {unsuccessful_list}")
    else:
        logging.info(f"All {total_websites} video(s) have been downloaded!")
