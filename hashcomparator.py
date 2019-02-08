from os import listdir, remove
import json
from pathlib import Path
from imagehash import hex_to_hash
from itertools import product
from imagehasher import ImageHasher


class HashComparator:
    def __init__(self, directory, old_images, max_diff=6):
        self.directory = directory
        self.hashes_file = '{}/hashes.json'.format(self.directory)
        self.old_images = old_images
        self.hashes = self.get_existing_hashes()
        self.max_diff = max_diff

    def get_existing_hashes(self):
        to_return = []
        if Path(self.hashes_file).is_file():
            with open(self.hashes_file, 'r') as f:
                for h in json.loads(f.read()):
                    to_return.append(hex_to_hash(h))
        return to_return

    def get_new_images(self):
        new_images = []
        for img in listdir(self.directory):
            if img not in self.old_images:
                new_images.append(img)
        return new_images

    def find_new_non_duplicates(self):
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
        duplicates = []
        duplicate_hashes = []

        new_images = self.find_new_non_duplicates()
        for h, img in product(self.hashes, new_images):
            try:
                new_hash = ImageHasher('{}/{}'.format(self.directory, img)).compute_hash()
                if h - new_hash <= self.max_diff:
                    duplicates.append(img)
                    duplicate_hashes.append(str(new_hash))
            except FileNotFoundError:
                pass

        for img in new_images:
            try:
                image_hash = ImageHasher('{}/{}'.format(self.directory, img)).compute_hash()
                if str(image_hash) not in duplicate_hashes:
                    self.hashes.append(image_hash)
            except FileNotFoundError:
                pass

        return duplicates

    def save_hashes(self):
        hashes_strings = [str(h) for h in self.hashes]
        with open(self.hashes_file, 'w') as f:
            f.write(json.dumps(hashes_strings))
