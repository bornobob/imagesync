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
    """
    The ImageDownloader class main functionality is to download images/GIFs from reddit.
    """
    def __init__(self, save_dir):
        """
        Creates an instance of the ImageDownloader class.
        :param save_dir: The directory where the images/GIFs will be saved.
        """
        self.save_dir = save_dir
        self.downloaded_images = []

    def download_image(self, url, filename):
        """
        This function downloads an image from a given URL and a filename.
        When the image is not a .jpg file, it will also convert it to .jpg.
        :param url: the URL where to download the image from.
        :param filename: the name given to the file.
        :return: the resulting path of the file.
        """
        try:
            img_req = requests.get(url)
            img_data = img_req.content
            req_ext = img_req.headers['content-type']
            img_ext = mt.guess_extension(req_ext)
            delete = False
            full_path = '{}/{}.{}'.format(self.save_dir, filename, img_ext)
            with open(full_path, 'wb') as handler:
                handler.write(img_data)
                if not img_ext == ".jpg":  # convert the image to jpg
                    Image.open(full_path).convert('RGB').save('{}/{}.jpg'.format(self.save_dir, filename))
                    delete = True
            if delete:
                os.remove(full_path)
            return '{}/{}.jpg'.format(self.save_dir, filename)
        except ConnectionError or OSError:
            raise Exception("Something went wrong downloading the image from " + url)

    @staticmethod
    def is_imgur_album(url):
        """
        Checks if a url is an imgur album link.
        :param url: The url to check.
        :return: True if the given url is an imgur album link.
        """
        match = re.match("(https?)://(www\.)?(?:m\.)?imgur\.com/(a|gallery)/([a-zA-Z0-9]+)(#[0-9]+)?", url)
        return bool(match)

    def download_reddit_images(self, reddit, time_filter='all', limit=100, min_score=0):
        """
        Downloads a number of images from a certain subreddit.
        Needs a file called credentials.json with the following info:
         - user_agent
         - client_id
         - client_secret
         - username
         - password
        :param reddit: the subreddit to download the images from.
        :param time_filter: the time filter to download from.
        :param limit: the maximum number of images to download.
        :param min_score: the minimum score of the posts.
        """
        with open('credentials.json', 'r') as f:
            credentials = loads(f.read())

        r = praw.Reddit(**credentials)

        counter = 0
        for post in r.subreddit(reddit).top(time_filter=time_filter, limit=limit):
            if not post.is_self and post.score >= min_score:
                url = post.url
                try:
                    if self.is_imgur_album(url):  # imgur album
                        downloader = ImgurAlbumDownloader(url)
                        downloader.save_images(self.save_dir)
                        self.downloaded_images.extend(downloader.downloaded_images)
                    if 'imgur.com' in url and url.endswith('.gifv'):  # imgur gif
                        downloaded_gif = GifDownloader.download_imgur_gif(url, self.save_dir)
                        if downloaded_gif:
                            self.downloaded_images.append(downloaded_gif)
                    elif 'imgur.com' in url and 'i.imgur' not in url:  # other imgur links
                        if url.endswith('.gifv'):  # gif
                            downloaded_gif = GifDownloader.download_imgur_gif(url, self.save_dir)
                            if downloaded_gif:
                                self.downloaded_images.append(downloaded_gif)
                        else:  # imgur image but not in i.imgur form
                            img_r = requests.get(url, headers={'User-agent': 'totally legit user agent'}).text
                            match = re.findall(r'<link +rel=\"image_src\" +href=\"([^\"]+)\"', img_r)
                            if match:
                                image_name = '{}-{}'.format(datetime.strftime(datetime.now(),
                                                                              '%d-%M-%Y--%H-%M-%S-%f'),
                                                            counter)
                                self.download_image(match[0], image_name)
                                self.downloaded_images.append('{}/{}.jpg'.format(self.save_dir, image_name))
                                counter += 1
                    elif 'gfycat.com' in url:  # gfycat link
                        downloaded_gif = GifDownloader.download_gfycat(url, self.save_dir)
                        if downloaded_gif:
                            self.downloaded_images.append(downloaded_gif)
                    else:  # hopefully just an image
                        image_name = '{}-{}'.format(datetime.strftime(datetime.now(),
                                                                      '%d-%M-%Y--%H-%M-%S-%f'),
                                                    counter)
                        self.download_image(url, image_name)
                        self.downloaded_images.append('{}/{}.jpg'.format(self.save_dir, image_name))
                        counter += 1
                except:  # this could be a wide range of exceptions
                    pass
