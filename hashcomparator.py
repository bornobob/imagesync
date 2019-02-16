from os import listdir, remove
import json
from pathlib import Path
from imagehash import hex_to_hash
from itertools import product
from imagehasher import ImageHasher


class HashComparator:
    """
    The HashComparator class makes use of the ImageHasher class in order to compare images in a directory to find
    duplicate images.
    """
    def __init__(self, directory, old_images, max_diff=6):
        """
        Creates an instance of the HashComparator class.
        :param directory: the directory to find and remove duplicates of.
        :param old_images: a list of images that were previously in the directory.
        :param max_diff: the maximum difference in bits two hashes may be to be treated equal (6-8ish)
        """
        self.directory = directory
        self.hashes_file = '{}/hashes.json'.format(self.directory)
        self.old_images = old_images
        self.hashes = self.get_existing_hashes()
        self.max_diff = max_diff

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

    def get_new_images(self):
        """
        Returns the images in a directory that are not in the old_images list.
        """
        new_images = []
        for img in listdir(self.directory):
            if img not in self.old_images:
                new_images.append(img)
        return new_images

    def find_new_non_duplicates(self):
        """
        Finds and removes duplicate duplicates of the NEW images (excluding the existing images).
        """
        new_images = []
        new_hashes = []
        added_images = self.get_new_images()
        for image in added_images:
            try:
                image_hash = ImageHasher('{}/{}'.format(self.directory, image)).compute_hash()
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
                remove('{}/{}'.format(self.directory, img))
        return new_images

    def find_new_duplicates(self):
        """
        Finds and removes duplicate new images by comparing them to the existing hashes.
        """
        duplicates = []
        duplicate_hashes = []

        # find and remove images
        new_images = self.find_new_non_duplicates()
        for h, img in product(self.hashes, new_images):
            try:
                new_hash = ImageHasher('{}/{}'.format(self.directory, img)).compute_hash()
                if h - new_hash <= self.max_diff:
                    duplicates.append(img)
                    duplicate_hashes.append(str(new_hash))
            except FileNotFoundError:
                pass

        # add new images to the existing hashes so they are saved for next time
        for img in new_images:
            try:
                image_hash = ImageHasher('{}/{}'.format(self.directory, img)).compute_hash()
                if str(image_hash) not in duplicate_hashes:
                    self.hashes.append(image_hash)
            except FileNotFoundError:
                pass

        return duplicates

    def save_hashes(self):
        """
        Saves the existing hashes in the hashes json file
        """
        hashes_strings = [str(h) for h in self.hashes]
        with open(self.hashes_file, 'w') as f:
            f.write(json.dumps(hashes_strings))
