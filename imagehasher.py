from PIL import Image
import imagehash
import pathlib


class ImageHasher:
    """
    A class used to hash images using imagehasher.
    """
    def __init__(self, path):
        """
        Creates an instance of the ImageHasher class.
        :param path: the path to the image to hash.
        """
        self.path = path
        self.image = None
        self.load_image()

    def compute_hash(self):
        """
        Computes the hash of the image using the phash algorithm.
        :return: the hash of the image.
        """
        if self.image:
            return imagehash.phash(self.image)
        else:
            raise FileNotFoundError()

    def load_image(self):
        """
        Loads the image on the given path.
        """
        try:
            if pathlib.Path(self.path).exists():
                self.image = Image.open(self.path)
        except OSError:
            pass
