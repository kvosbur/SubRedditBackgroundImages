import os
import ctypes
import requests
from PIL import Image

base_directory = os.path.dirname(os.path.abspath(__file__))

def get_screen_size():
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def get_screen_aspect_ratio():
    screen_size = get_screen_size()
    return screen_size[0] / screen_size[1]


def image_correct_aspect(image_file_path):
    # get screen size to resize to
    # user32 = ctypes.windll.user32
    # screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    image = Image.open(image_file_path)
    image_size = image.size
    print(image_size)
    if image_size[0] >= image_size[1]:
        return True, image_size
    else:
        return False, image_size


def get_file_from_url(dest_directory, dest_file_name,  file_url, check_correct_aspect=True):
    valid_extensions = ["png", "jpg"]
    ext = file_url.split(".")[-1]
    if ext not in valid_extensions:
        return ""
    response = requests.get(file_url)
    response.raise_for_status()

    content = response.content

    file_name = dest_file_name + "." + ext
    file_path = os.path.join(dest_directory, file_name)
    final_path = os.path.join(dest_directory, "final." + ext)

    print("File Saved at " + file_path)
    with open(file_path, "wb") as f:
        f.write(content)

    is_correct_aspect, image_size = image_correct_aspect(file_path)
    if check_correct_aspect:
        if is_correct_aspect:
            return file_path, final_path, image_size
        else:
            os.remove(file_path)
            return "", "", image_size
    else:
        return file_path, final_path, image_size
