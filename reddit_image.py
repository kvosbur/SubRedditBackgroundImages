import requests
from tempfile import mkstemp
from PIL import Image
import shutil
import os
import ctypes
from urllib.parse import quote
from reddit_logging import log
from Model.images import Images
import datetime


class RedditImage:

    HEIGHT = 0
    WIDTH = 1
    validImageTypes = ["png", "jpg"]

    def __init__(self, imageUrl, submissionUrl):
        self.imageUrl = imageUrl
        self.submissionUrl = submissionUrl
        self.imagePath = ""
        self._imageWidth = 0
        self._imageHeight = 0
        self.ext = ""
        self.destDirectory = ""
        self.imageObj = None

    def __str__(self):
        return "URL: " + self.imageUrl + "  FilePath:" + self.imagePath + "  Height:" + str(self.imageHeight)

    @property
    def imageHeight(self):
        if self._imageHeight == 0 and self.imagePath != "":
            image = Image.open(self.imagePath)
            self.imageWidth, self.imageHeight = image.size
        return self._imageHeight

    @imageHeight.setter
    def imageHeight(self, val):
        self._imageHeight = val

    @property
    def imageWidth(self):
        if self._imageWidth == 0 and self.imagePath != "":
            image = Image.open(self.imagePath)
            self.imageWidth, self.imageHeight = image.size
        return self._imageWidth

    @imageWidth.setter
    def imageWidth(self, val):
        self._imageWidth = val

    @staticmethod
    def get_size_data(imageObject, size_type):
        if size_type == RedditImage.WIDTH:
            return imageObject.imageWidth
        elif size_type == RedditImage.HEIGHT:
            return imageObject.imageHeight

    def create_image_model(self):
        self.imageObj = Images(self.submissionUrl, self.imagePath, datetime.datetime.now(), None)

    def safe_submissionUrl(self):
        return quote(self.submissionUrl)

    def safe_imageUrl(self):
        return quote(self.imageUrl)

    def get_image_path(self):
        if self.imagePath == "":
            # need to save image to a file
            a = 3

        return self.imagePath

    def image_is_landscape(self):
        # get screen size to resize to
        # user32 = ctypes.windll.user32
        # screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

        if self.imageWidth > self.imageHeight:
            return True
        else:
            return False

    def get_image_from_url(self, destDirectory):

        self.destDirectory = destDirectory
        ext = self.imageUrl.split(".")[-1]
        self.ext = ext
        if ext not in RedditImage.validImageTypes:
            return

        if self.imagePath != "":
            return

        response = requests.get(self.imageUrl)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            log("There was an exception thrown while getting url HTTP Status:", response.status_code)
            return

        content = response.content

        descriptor, self.imagePath = mkstemp(suffix="." + ext, dir=destDirectory)

        #print("File Saved at " + self.imagePath)
        with os.fdopen(descriptor, "wb") as imageFile:
            imageFile.write(content)

    def save_image_to_final_path(self):
        final_path = os.path.join(self.destDirectory, "final." + self.ext)
        shutil.move(self.imagePath, final_path)
        self.imagePath = ""
        return final_path

    @staticmethod
    def set_image_to_desktop_background(image_path):
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 0)

    def set_to_desktop_background(self):
        final_path = self.save_image_to_final_path()
        RedditImage.set_image_to_desktop_background(final_path)

    def cleanup(self):
        if self.imagePath != "" and os.path.exists(self.imagePath):
            os.remove(self.imagePath)

    def image_downloaded(self):
        return self.imagePath != ""

    def move_to_folder(self, folder):
        _, name = os.path.split(self.imagePath)
        shutil.copy(self.imagePath, os.path.join(folder, name))


