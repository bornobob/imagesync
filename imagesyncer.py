from hashcomparator import HashComparator
from imagedownloader import ImageDownloader
from os import listdir, remove, mkdir
from pathlib import Path


class ImageSyncer:
    def __init__(self, path, reddits):
        self.path = path
        self.reddits = reddits
        if not Path(self.path).is_dir():
            mkdir(self.path)

    def sync(self):
        old_images = listdir(self.path)
        hc = HashComparator(self.path, old_images)

        downloader = ImageDownloader(self.path)
        for r in self.reddits:
            downloader.download_reddit_images(**r)

        for img in hc.find_new_duplicates():
            try:
                remove('{}/{}'.format(self.path, img))
            except:
                pass

        hc.save_hashes()
