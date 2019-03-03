import re
import requests
import ffmpy
from datetime import datetime
import os


GFY_INFO_LINK = 'https://gfycat.com/cajax/get'


def convert_to_gif(path):
    """
    Converts a given video to the gif format.
    Uses FFmpeg.
    :param path: the path to the video to convert.
    """
    new_path = path[:path.rfind('.') + 1] + 'gif'
    ff = ffmpy.FFmpeg(
        inputs={path: None},
        outputs={new_path: None}
    )
    ff.run()
    os.remove(path)
    return new_path


class GifDownloader:
    """
    A small class containing static methods used to download GIFs from a number of sources.
    """
    @staticmethod
    def download_gfycat(url, folder):
        """
        Downloads a gif from gfycat.
        :param url: the gfycat url.
        :param folder: the folder to save the gif into.
        """
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
                return convert_to_gif(filename)

    @staticmethod
    def download_imgur_gif(url, folder):
        """
        Downloads a gif from imgur.
        :param url: the imgur gif url.
        :param folder: the folder to save the gif into.
        """
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
        return convert_to_gif(filename)
