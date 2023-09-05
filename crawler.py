import argparse
import logging
import os

from basic import set_headers
from bv_crawler import crawl_user_all_video, crawl_bv_list
from ep_crawler import crawl_episodes


def parse_arguments() -> argparse.Namespace:
    """
    Parse the arguments.
    """
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-u", "--uid", type=str,
                       required=False, help="The uid of the poster.")
    group.add_argument("-b", "--bvid", type=str, required=False,
                       help="The bvid of the video.")
    group.add_argument("-e", "--epid", type=str, required=False,
                       help="The beginning id of an episode you want to crawl.")
    parser.add_argument("-n", "--num", type=int, default=1,
                        help="The number of episodes to download.")
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
    if not os.path.exists(args.download_addr):
        os.makedirs(args.download_addr)
    if args.uid:
        crawl_user_all_video(args.uid, headers, args.download_addr,
                             args.quality_v, args.quality_a)
    elif args.bvid:
        crawl_bv_list([args.bvid], headers, args.download_addr,
                      args.quality_v, args.quality_a)
    elif args.epid:
        crawl_episodes(args.epid, args.num, headers, args.download_addr,
                       args.quality_v, args.quality_a)
    else:
        logging.error("Please specify the uid or bvid or epid!")
