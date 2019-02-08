import re
import requests
import ffmpy
from datetime import datetime
import os


GFY_INFO_LINK = 'https://gfycat.com/cajax/get'


def convert_to_gif(path):
    new_path = path[:path.rfind('.') + 1] + 'gif'
    ff = ffmpy.FFmpeg(
        inputs={path: None},
        outputs={new_path: None}
    )
    ff.run()
    os.remove(path)


class GifDownloader:
    @staticmethod
    def download_gfycat(url, folder):
        res = re.findall(r'https?://(?:www\.)?gfycat\.com/([a-zA-Z]+)', url)
        if res:
            gif_id = res[0]
            gfy_url = '{}/{}'.format(GFY_INFO_LINK, gif_id)
            r = requests.get(gfy_url).json()
            if 'gfyItem' in r.keys():
                mp4_url = r['gfyItem']['mp4Url'].encode('utf-8').decode('unicode_escape')
                filename = '{}/{}-{}.{}'.format(folder,
                                                gif_id,
                                                datetime.strftime(datetime.now(), '%d-%M-%Y--%H-%M-%S-%f'),
                                                'mp4')
                with open(filename, 'wb') as f:
                    vid = requests.get(mp4_url, stream=True)
                    for chunk in vid.iter_content(chunk_size=1024*1024):
                        if chunk:
                            f.write(chunk)
                convert_to_gif(filename)

    @staticmethod
    def download_imgur_gif(url, folder):
        r = requests.get(url[:-1], stream=True)
        code = re.findall(r'\.com/([^.]+)', url)[0]
        filename = '{}/{}-{}.{}'.format(folder,
                                        code,
                                        datetime.strftime(datetime.now(), '%d-%m-%Y--%H-%M-%S-%f'),
                                        'webm')
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        convert_to_gif(filename)
