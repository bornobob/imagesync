import requests
from PIL import Image
import re
import os
import mimetypes as mt
from albumdownloader import ImgurAlbumDownloader
from datetime import datetime
import praw
from json import loads
from gifdownloader import GifDownloader


class ImageDownloader:
    def __init__(self, save_dir):
        self.save_dir = save_dir

    def download_image(self, url, filename):
        try:
            img_req = requests.get(url)
            img_data = img_req.content
            req_ext = img_req.headers['content-type']
            img_ext = mt.guess_extension(req_ext)
            delete = False
            full_path = '{}/{}.{}'.format(self.save_dir, filename, img_ext)
            with open(full_path, 'wb') as handler:
                handler.write(img_data)
                if not img_ext == ".jpg":
                    Image.open(full_path).convert('RGB').save('{}/{}.jpg'.format(self.save_dir, filename))
                    delete = True
            if delete:
                os.remove(full_path)
            return '{}/{}.jpg'.format(self.save_dir, filename)
        except ConnectionError or OSError:
            raise Exception("Something went wrong downloading the image from " + url)

    @staticmethod
    def is_imgur_album(url):
        match = re.match("(https?)://(www\.)?(?:m\.)?imgur\.com/(a|gallery)/([a-zA-Z0-9]+)(#[0-9]+)?", url)
        return bool(match)

    def download_reddit_images(self, reddit, sort='all', limit=100, min_score=0):
        with open('credentials.json', 'r') as f:
            credentials = loads(f.read())

        r = praw.Reddit(**credentials)
        try:
            counter = 0
            for post in r.subreddit(reddit).top(time_filter=sort, limit=limit):
                if not post.is_self and post.score >= min_score:
                    url = post.url
                    try:
                        if self.is_imgur_album(url):
                            downloader = ImgurAlbumDownloader(url)
                            downloader.save_images(self.save_dir)
                        if 'imgur.com' in url and url.endswith('.gifv'):
                            GifDownloader.download_imgur_gif(url, self.save_dir)
                        elif 'imgur.com' in url and 'i.imgur' not in url:
                            if url.endswith('.gifv'):
                                GifDownloader.download_imgur_gif(url, self.save_dir)
                            else:
                                img_r = requests.get(url, headers={'User-agent': 'totally legit user agent'}).text
                                match = re.findall(r'<link +rel=\"image_src\" +href=\"([^\"]+)\"', img_r)
                                if match:
                                    self.download_image(match[0], '{}-{}'.format(
                                        datetime.strftime(datetime.now(),
                                                          '%d-%M-%Y--%H-%M-%S-%f'),
                                        counter))
                                    counter += 1
                        elif 'gfycat.com' in url:
                            GifDownloader.download_gfycat(url, self.save_dir)
                        else:
                            self.download_image(url, '{}-{}'.format(datetime.strftime(datetime.now(),
                                                                                      '%d-%M-%Y--%H-%M-%S-%f'),
                                                                    counter))
                            counter += 1
                    except:
                        pass
        except KeyError:
            pass
