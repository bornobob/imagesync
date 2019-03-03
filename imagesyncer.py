from hashcomparator import HashComparator
from imagedownloader import ImageDownloader
from os import mkdir
from pathlib import Path


class ImageSyncer:
    """
    A class that contains a function to sync images from reddits.
    Checks for duplicate images using the HashComparator class.
    Input is supplied as a list of dictionaries containing the reddits to download images form.
    See the documentation for the __init__ function for more information.
    """
    def __init__(self, path, reddits):
        """
        Creates an instance of the ImageSyncer class, requires a directory to save the images into and a list of
        dictionaries containing the following keys:
         - "reddit" (the reddit you want to download images from)
         - "time_filter" (the time filter you want applied to get the top posts of)
                         (one of all, day, hour, month, week, year)
         - "limit" (the maximum number of posts to download (max. 100))
         - "min_score" (the minimum score the posts need to be downloaded)
        :param path: the path to save the images/GIFs into.
        :param reddits: the reddits as a list of dictionaries described above.
        """
        self.path = path
        self.reddits = reddits
        if not Path(self.path).is_dir():
            mkdir(self.path)

    def sync(self):
        """
        Synchronizes the images as described in the __init__ function using the HashComparator and ImageDownloader.
        """
        downloader = ImageDownloader(self.path)
        for r in self.reddits:
            downloader.download_reddit_images(**r)

        hc = HashComparator(self.path, downloader.downloaded_images)
        hc.remove_duplicates()

        hc.save_hashes()
