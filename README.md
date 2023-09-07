# Bilibili_video_crawler
This is a crawler for Bilibili videos. It can download videos from Bilibili and save them to your local disk. 

Given a user `uid`, it can download all the post videos of this user. Given a video `bvid`, it can download this video. Given a episode `epid` and `num`, it can download `num` videos beginning at this episode.

The quality of videos or audios can be specified.
## Requirements
You need to install the following packages:
```txt
beautifulsoup4
requests
lxml
```
They have already been listed in the requirements.txt file, so you can install them by running the following command:

```bash
conda create -n crawler python=3.10
conda activate crawler
git clone git@github.com:ljj21/Bilibili_video_crawler.git
cd Bilibili_video_crawler
pip install -r requirements.txt
```
By the way, you need to install **[ffmpeg](https://www.ffmpeg.org/)** to mix the video and audio files.
## Usage
### Config your cookies
Before using this crawler, you need to config your cookies. You can get your cookies by logging in to Bilibili and pressing `F12` to open the developer tools. Then you need to create a file named `config.json` in the root directory of this repository. The content of `config.json` should be like this:
```json
{
    "cookie": "<your cookie>"
}
```
### Download a video by its `bvid`
Here is an example of downloading a video by its `bvid`:
```bash
python crawler.py -b BV13p4y1V7Z7 -v 360p -a 64k
```
The `-b` option specifies the `bvid` of the video. The `-v` option specifies the video quality. The `-a` option specifies the audio quality. The video quality can be `360p`, `480p`, `720p` or `1080p`. The audio quality can be `64k`, `132k`, `192k`. The default video quality is `720p` and the default audio quality is `132k`. 
The video will be saved to `./download/` directory by default. You can change the directory by using the `-d` option.
Here is the running log:
```txt
2023-08-06 19:20:42,054 - INFO - Total number of sites crawled: 1.
2023-08-06 19:20:42,620 - INFO - Crawling 1/1 - 博人传：第二部来袭，博人佐良娜造型曝光，向日葵恐怕有大能力！.
2023-08-06 19:20:43,068 - INFO - Downloading video file: 博人传：第二部来袭，博人佐良娜造型曝光，向日葵恐怕有大能力！_video.m4s.
2023-08-06 19:20:43,493 - INFO - 博人传：第二部来袭，博人佐良娜造型曝光，向日葵恐怕有大能力！_video.m4s downloaded!
2023-08-06 19:20:43,757 - INFO - Downloading audio file: 博人传：第二部来袭，博人佐良娜造型曝光，向日葵恐怕有大能力！_audio.m4s.
2023-08-06 19:20:43,867 - INFO - 博人传：第二部来袭，博人佐良娜造型曝光，向日葵恐怕有大能力！_audio.m4s downloaded!
2023-08-06 19:20:43,934 - INFO - Video and audio have been mixed!
2023-08-06 19:20:43,935 - INFO - Finished 1/1 - 博人传：第二部来袭，博人佐良娜造型曝光，向日葵恐怕有大能力！.
2023-08-06 19:20:43,936 - INFO - All 1 video(s) have been downloaded!
```
### Download all the videos of a user by its `uid`
Here is an example of downloading all the videos of a user by its `uid`:
```bash
python crawler.py -u 174881400
```
The `-u` option specifies the `uid` of the user. The videos will be saved to `./download/<uid>` directory by default. You can change the directory by using the `-d` option.
### Download a video by its `epid` and `num`
Here is an example of downloading a video by its `epid` and `num`:
```bash
python crawler.py -e 469113 -n 3
```
The `-e` option specifies the `epid` of the video. The `-n` option specifies the number of videos to be downloaded. By default, `-n` is one. The videos will be saved to `./download/<epid>` directory by default. You can change the directory by using the `-d` option.
**Of course, The `-b`, `-u` and `-e` options cannot be used at the same time.**
## Attention
+ This repository is only for learning and communication. Please do not use it for commercial purposes.
+ If you think your behaviors maybe consume too much resources of Bilibili, please check the [Bilibili robots.txt](https://www.bilibili.com/robots.txt) file beforehand.
+ The cookie should be updated regularly. If you find that the crawler cannot work, please update your cookie.
+ This repository is just a toy. It is not robust enough or tested enough. 
+ If you find any bugs, please feel free to contact me.