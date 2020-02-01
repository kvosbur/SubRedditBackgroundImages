import os
import ctypes
from PIL import ImageDraw
import configparser
import random

base_directory = os.path.dirname(os.path.abspath(__file__))


def init_directories():
    pictureDirectory = os.path.join(base_directory, "PictureSource")
    if not os.path.exists(pictureDirectory):
        os.mkdir(pictureDirectory)

    lockScreenDirectory = os.path.join(pictureDirectory, "LockScreen")
    if not os.path.exists(lockScreenDirectory):
        os.mkdir(lockScreenDirectory)


def remove_all_files(directory):
    prev = os.listdir(directory)
    for f in prev:
        full = os.path.join(directory, f)
        os.remove(full)


def get_random_url(url_list):
    url = random.choice(url_list)
    url_list.remove(url)
    return url, url_list


def print_list(l):
    print("[")
    index = 0
    for item in l:
        print(index, str(item), ",")
        index += 1
    print("]")


def readConfigFile():
    config_file_path = os.path.join(base_directory, "config.ini")
    config = configparser.ConfigParser()
    config.read(config_file_path)
    return config


def get_screen_size():
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def get_screen_aspect_ratio():
    screen_size = get_screen_size()
    return screen_size[0] / screen_size[1]


RIGHT = 0
LEFT = 1


def average_pixel_color(image_object, side):
    r = 0
    g = 0
    b = 0
    width, height = image_object.size
    w = 0
    if side == RIGHT:
        w = width - 1
    for h in range(height):
        pixel= image_object.getpixel((w, h))
        if len(pixel) == 3:
            nextR, nextG, nextB = pixel
        # ignore alpha if it is given
        elif len(pixel) == 4:
            nextR, nextG, nextB, _ = pixel
        r += nextR
        g += nextG
        b += nextB

    return round(r / height), round(g / height), round(b / height)


def do_gradient(image_obj, upperLeft, lowerRight, leftColor, rightColor):
    drawer = ImageDraw.Draw(image_obj)
    distance_x = lowerRight[0] - upperLeft[0]
    diff_r = leftColor[0] - rightColor[0]
    diff_g = leftColor[1] - rightColor[1]
    diff_b = leftColor[2] - rightColor[2]
    for x_diff in range(distance_x):
        x = upperLeft[0] + x_diff
        percent_dist = x_diff / distance_x
        colorR = round(leftColor[0] - (percent_dist * diff_r))
        colorG = round(leftColor[1] - (percent_dist * diff_g))
        colorB = round(leftColor[2] - (percent_dist * diff_b))
        drawer.line((x, upperLeft[1], x, lowerRight[1]), fill=(colorR, colorG, colorB))


