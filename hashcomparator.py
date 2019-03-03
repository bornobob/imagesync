from os import listdir, remove
import json
from pathlib import Path
from imagehash import hex_to_hash
from itertools import product, zip_longest
from imagehasher import ImageHasher
from threading import Thread


def list_chunks(lst, n):
    """
    Splits a list in n parts.
    From: https://stackoverflow.com/questions/2130016
    """
    return [lst[i::n] for i in range(n)]


class HashComparatorThread(Thread):
    """
    A Thread instance to multi-thread the process of creating hashes and comparing them to existing hashes.
    """
    def __init__(self, to_compare, result_dict, existing_hashes, max_diff):
        """
        Creates an instance of the HashComparatorThread class.
        :param to_compare: list of images (paths) to compare.
        :param result_dict: the resulting dictionary.
        :param existing_hashes: the existing hashes to compare against.
        :param max_diff: the maximum difference in bits two hashes may be to be treated equal (6-8ish)
        """
        Thread.__init__(self)
        self.to_compare = to_compare
        self.result_dict = result_dict
        self.existing_hashes = existing_hashes
        self.max_diff = max_diff

    def init_new_hashes(self):
        """
        Hashes the images the Thread should compare.
        """
        for img in self.to_compare:
            try:
                img_hash = ImageHasher(img).compute_hash()
                self.result_dict[img] = HashBoolValue(img_hash)
            except FileNotFoundError:
                pass

    def run(self):
        """
        Initiates the hashes and compares them to the existing hashes.
        Marks and removes duplicate images.
        """
        self.init_new_hashes()
        for img, old_hash in product(self.to_compare, self.existing_hashes):
            if img in self.result_dict.keys():
                if self.result_dict[img].image_hash - old_hash <= self.max_diff:
                    self.result_dict[img].duplicate = True
                    remove(img)


class HashBoolValue:
    """
    A small class to store both a hash object and a boolean value
    """
    def __init__(self, image_hash, value=False):
        self.image_hash = image_hash
        self.duplicate = value


class HashComparator:
    """
    The HashComparator class makes use of the ImageHasher class in order to compare images in a directory to find
    duplicate images.
    """
    def __init__(self, directory, new_images, threads=4, max_diff=6):
        """
        Creates an instance of the HashComparator class.
        :param directory: the directory to find and remove duplicates of.
        :param new_images: the list of images that have been added to the directory.
        :param threads: number of threads used to compare hashes
        :param max_diff: the maximum difference in bits two hashes may be to be treated equal (6-8ish)
        """
        self.directory = directory
        self.hashes_file = '{}/hashes.json'.format(self.directory)
        self.new_images = new_images
        self.hashes = self.get_existing_hashes()
        self.max_diff = max_diff
        self.threads = threads

    def get_existing_hashes(self):
        """
        Returns the existing hashes saved in the hashes json file if there are any.
        """
        to_return = []
        if Path(self.hashes_file).is_file():
            with open(self.hashes_file, 'r') as f:
                for h in json.loads(f.read()):
                    to_return.append(hex_to_hash(h))
        return to_return

    def find_new_non_duplicates(self):
        """
        Finds and removes duplicate duplicates of the NEW images (excluding the existing images).
        """
        new_images = []
        new_hashes = []
        added_images = self.new_images
        for image in added_images:
            try:
                image_hash = ImageHasher(image).compute_hash()
                found = False
                for h in new_hashes:
                    diff = image_hash - h
                    if diff <= self.max_diff:
                        found = True
                if not found:
                    new_hashes.append(image_hash)
                    new_images.append(image)
            except FileNotFoundError or ValueError:
                pass
        for img in added_images:
            if img not in new_images:
                remove(img)
        return new_images

    def remove_duplicates(self):
        """
        Finds and removes duplicate new images by comparing them to the existing hashes.
        """
        new_images = self.find_new_non_duplicates()  # find the NEW images
        new_hashes = {}  # dictionary to save image-hash combos and track if they are a duplicate

        partitioned_new_images = list(list_chunks(new_images, self.threads))

        threads = []  # create and start and join threads
        for i in range(self.threads):
            t = HashComparatorThread(partitioned_new_images[i], new_hashes, self.hashes, self.max_diff)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        for k in new_hashes.keys():  # save non duplicates to current hashes
            if not new_hashes[k].duplicate:
                self.hashes.append(new_hashes[k].image_hash)

    def save_hashes(self):
        """
        Saves the existing hashes in the hashes json file
        """
        hashes_strings = [str(h) for h in self.hashes]
        with open(self.hashes_file, 'w') as f:
            f.write(json.dumps(hashes_strings))
