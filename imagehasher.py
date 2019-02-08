from PIL import Image
import imagehash
import pathlib


class ImageHasher:
    def __init__(self, path):
        self.path = path
        self.image = None
        self.load_image()

    def compute_hash(self):
        if self.image:
            return imagehash.phash(self.image)
        else:
            raise FileNotFoundError()

    def load_image(self):
        try:
            if pathlib.Path(self.path).exists():
                self.image = Image.open(self.path)
        except OSError:
            pass
