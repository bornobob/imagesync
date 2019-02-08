import re
import urllib.request
import urllib.parse
import urllib.error
import os
import math
from collections import Counter


"""
Copyright (C) 2012 Alex Gisby

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the 
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the following conditions: 

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the 
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE 
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


class ImgurAlbumException(Exception):
    def __init__(self, msg=''):
        self.msg = msg


class ImgurAlbumDownloader:
    def __init__(self, album_url):
        self.album_url = album_url
        self.image_callbacks = []

        match = re.match("(https?)://(www\.)?(?:m\.)?imgur\.com/(a|gallery)/([a-zA-Z0-9]+)(#[0-9]+)?", album_url)
        if not match:
            raise ImgurAlbumException("URL must be a valid Imgur Album")

        self.protocol = match.group(1)
        self.album_key = match.group(4)

        full_list_url = "http://imgur.com/a/" + self.album_key + "/layout/blog"

        try:
            self.response = urllib.request.urlopen(url=full_list_url)
            response_code = self.response.getcode()
        except:
            response_code = 404
            self.response = False

        if not self.response or self.response.getcode() != 200:
            raise ImgurAlbumException("Error reading Imgur: Error Code %d" % response_code)

        html = self.response.read().decode('utf-8')
        self.imageIDs = re.findall('.*?{"hash":"([a-zA-Z0-9]+)".*?"ext":"(\.[a-zA-Z0-9]+)".*?', html)

        self.cnt = Counter()
        for i in self.imageIDs:
            self.cnt[i[1]] += 1

    def num_images(self):
        return len(self.imageIDs)

    def list_extensions(self):
        return self.cnt.most_common()

    def album_key(self):
        return self.album_key

    def save_images(self, folder_name=False):
        self.imageIDs = list(set(self.imageIDs))

        if folder_name:
            album_folder = folder_name
        else:
            album_folder = self.album_key

        if not os.path.exists(album_folder):
            os.makedirs(album_folder)

        # And finally loop through and save the images:
        for (counter, image) in enumerate(self.imageIDs, start=1):
            image_url = "http://i.imgur.com/" + image[0] + image[1]

            prefix = "%0*d-" % (
                int(math.ceil(math.log(len(self.imageIDs) + 1, 10))),
                counter
            )
            path = os.path.join(album_folder, prefix + image[0] + image[1])

            # Run the callbacks:
            for fn in self.image_callbacks:
                fn(counter, image_url, path)

            # Actually download the thing
            if not os.path.isfile(path):
                try:
                    urllib.request.urlretrieve(image_url, path)
                except:
                    os.remove(path)
