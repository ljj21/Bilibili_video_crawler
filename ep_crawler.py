import requests
import json
from typing import Dict
import logging
import os

from basic import download_and_mix, get_quality_str


def get_eps_info(ep_id: str, num: int, headers, download_addr: str) -> None:
    """
    Get the episodes info (ep_id and title) of a bangumi according to the beginning `ep_id`, and save it to a json file.

    Args:
        ep_id: The beginning id of the bangumi.
        num: The number of episodes to download.
    """
    logging.info(f"Start Collecting {ep_id}'s episodes info.")
    url = f"https://api.bilibili.com/pgc/view/web/season?ep_id={ep_id}"
    resp = requests.get(url=url, headers=headers).json()
    episodes_info_list = resp['result']['episodes']
    ep_id_list = [str(ep['ep_id']) for ep in episodes_info_list]
    title_list = [ep['share_copy'] for ep in episodes_info_list]
    begin_index = ep_id_list.index(ep_id)
    ep_id_list = ep_id_list[begin_index: begin_index + num]
    title_list = title_list[begin_index: begin_index + num]
    ep_list = [{"id": ep_id, "title": title}
               for ep_id, title in zip(ep_id_list, title_list)]
    with open(download_addr + "video_list.json", "w", encoding="utf-8") as f:
        json.dump(ep_list, f)
    logging.info(f"Finished Collecting {ep_id}'s episodes info.")


def get_download_url(ep_id: str, headers, video_id: str, audio_id: str, title: str) -> Dict:
    url = f"https://api.bilibili.com/pgc/player/web/v2/playurl?fnval=4048&fourk=1&ep_id={ep_id}"
    resp = requests.get(url=url, headers=headers).json()
    info = dict()
    video_info = resp['result']['video_info']['dash']['video']
    for video in video_info:
        if video['baseUrl'].find(video_id + ".m4s") != -1:
            info['video_url'] = video['baseUrl']
            break
    audio_info = resp['result']['video_info']['dash']['audio']
    for audio in audio_info:
        if audio['baseUrl'].find(audio_id + ".m4s") != -1:
            info['audio_url'] = audio['baseUrl']
            break
    info["title"] = title
    return info


def crawl_episodes(ep_id: str, num: int, headers, download_addr: str, quality_v: str, quality_a: str) -> None:
    """
    Crawl the episodes of a bangumi and download them.

    Args:
        ep_id: The beginning id of the bangumi.
        num: The number of episodes to download.
    """
    download_addr = download_addr + ep_id + "/"
    if not os.path.exists(download_addr):
        os.makedirs(download_addr)
    get_eps_info(ep_id, num, headers, download_addr)
    quality_v, quality_a = get_quality_str(quality_v, quality_a)
    with open(download_addr + "video_list.json", "r", encoding="utf-8") as f:
        ep_list = json.load(f)
    total_num = len(ep_list)
    if total_num == 0:
        logging.warning(f"Bangumi {ep_id} has no episode.")
        return
    logging.info(f"Total number of episodes: {total_num}")
    unsuccessful_list = []
    for index, ep in enumerate(ep_list, start=1):
        logging.info(f"Downloading {index}/{total_num}.")
        try:
            info = get_download_url(ep['id'], headers, quality_v, quality_a, ep['title'])
            download_and_mix(info, headers, download_addr)
            logging.info(f"Finished {index}/{total_num}.")
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                logging.error(
                    "Keyboard interrupt detected. The program will exit.")
                break
            else:
                logging.warning(
                    f"Failed to download {index}/{total_num}.")
                unsuccessful_list.append(index - 1)
    if len(unsuccessful_list) > 0:
        logging.warning(
            f"Failed to crawl {len(unsuccessful_list)}/{total_num} video(s).")
        logging.warning(f"Unsuccessful list: {unsuccessful_list}")
    else:
        logging.info(f"All {total_num} video(s) have been downloaded!")