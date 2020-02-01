import requests
from tempfile import mkstemp
from PIL import Image
import ctypes
import shutil
import os


class RedditImage:

    validImageTypes = ["png", "jpg"]

    def __init__(self, imageUrl, submissionUrl):
        self.imageUrl = imageUrl
        self.submissionUrl = submissionUrl
        self.imagePath = ""
        self.imageWidth = 0
        self.imageHeight = 0
        self.ext = ""
        self.destDirectory = ""


    def get_image_path(self):
        if self.imagePath == "":
            # need to save image to a file
            a = 3

        return self.imagePath


    def image_is_landscape(self):
        # get screen size to resize to
        # user32 = ctypes.windll.user32
        # screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

        if self.imageHeight == 0 or self.imageWidth == 0:
            image = Image.open(self.imagePath)
            self.imageWidth, self.imageHeight = image.size
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
        response.raise_for_status()

        content = response.content

        descriptor, self.imagePath = mkstemp(suffix="." + ext, dir=destDirectory)

        print("File Saved at " + self.imagePath)
        with os.fdopen(descriptor, "wb") as imageFile:
            imageFile.write(content)

    def save_image_to_final_path(self):
        final_path = os.path.join(self.destDirectory, "final." + self.ext)
        shutil.move(self.imagePath, final_path)
        self.imagePath = ""
        return final_path

    def set_file_to_desktop_background(self):
        final_path = self.save_image_to_final_path()

        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, final_path, 0)

    def cleanup(self):
        if self.imagePath != "":
            os.remove(self.imagePath)


    def image_downloaded(self):
        return self.imagePath != ""


