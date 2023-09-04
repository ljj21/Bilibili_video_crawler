import requests
from bs4 import BeautifulSoup as BS
import json
from typing import List, Dict
import re
import subprocess
import logging
import os
import argparse

from bilibili_crawler import set_headers, download_file

def get_eps_info(ep_id: str, num: int, headers, download_addr: str) -> None:
    """
    Get the episodes info (ep_id and title) of a bangumi according to the beginning `ep_id`, and save it to a json file.

    Args:
        ep_id: The beginning id of the bangumi.
        num: The number of episodes to download.
    """
    url = f"https://api.bilibili.com/pgc/view/web/season?ep_id={ep_id}"
    resp = requests.get(url=url, headers=headers).json()
    episodes_info_list = resp['result']['episodes']
    ep_id_list = [str(ep['ep_id']) for ep in episodes_info_list]
    title_list = [ep['share_copy'] for ep in episodes_info_list]
    begin_index = ep_id_list.index(ep_id)
    ep_id_list = ep_id_list[begin_index : begin_index + num]
    title_list = title_list[begin_index : begin_index + num]
    ep_list = [{"ep_id": ep_id, "title": title} for ep_id, title in zip(ep_id_list, title_list)]
    with open(download_addr + "episode_list.json", "w", encoding="utf-8") as f:
        json.dump(ep_list, f)

def get_download_url(ep_id: str) -> str:
    url = f"https://api.bilibili.com/pgc/player/web/playurl?ep_id={ep_id}"
    resp = requests.get(url=url, headers=headers)
    download_url = resp.json()['result']['durl'][0]['url']
    return download_url

def parse_arguments() -> argparse.Namespace:
    """
    Parse the arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--epid", type=str, help="The uid of the user.")
    parser.add_argument("-n", "--num", type=int, default=1, help="The number of episodes to download.")
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
    if args.epid:
        if not os.path.exists(args.download_addr):
            os.makedirs(args.download_addr)
        get_eps_info(args.epid, args.num, headers, args.download_addr)
        with open(args.download_addr + "episode_list.json", "r", encoding="utf-8") as f:
            ep_list = json.load(f)
        for ep in ep_list:
            download_url = get_download_url(ep['ep_id'])
            logging.info(f"Downloading {ep['title']}...")
            download_file(download_url, ep['title'], ".mp4", headers, args.download_addr)
    else:
        logging.error("Please specify the uid or bvid!")
   
