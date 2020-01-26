import praw, os
from dotenv import load_dotenv
import configparser
import random
import requests
import ctypes
from PIL import Image

load_dotenv('.env')

def get_submissions_for_subreddit(reddit_obj, subreddit_name, time_filter="day", nsfw_allowed=False):
    submissions = reddit_obj.subreddit(subreddit_name).top(time_filter)
    image_urls = []

    for sub in submissions:
        '''
        print(sub)
        print(sub.title)
        print(sub.permalink)
        print(sub.over_18)
        print(sub.url)
        '''
        # parse
        if sub.url != '':
            image_urls.append(sub.url)
    return image_urls


def save_url_list(url_list):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "PictureSource", "url_list.txt"), "w") as f:
        for url in url_list:
            f.write(url + "\n")


def get_random_url(url_list):
    url = random.choice(url_list)
    url_list.remove(url)
    return url, url_list


def get_file_from_url(file_url):
    valid_extensions = ["png", "jpg"]
    response = requests.get(file_url)
    response.raise_for_status()

    content = response.content
    ext = file_url.split(".")[-1]
    if ext not in valid_extensions:
        return ""
    file_name = "temp." + ext
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PictureSource", file_name)

    with open(file_path, "wb") as f:
        f.write(content)

    is_correct_aspect = image_correct_aspect(file_path)
    if is_correct_aspect:
        return file_path
    else:
        return ""


def image_correct_aspect(file_path):
    # get screen size to resize to
    # user32 = ctypes.windll.user32
    # screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    image = Image.open(file_path)
    image_size = image.size
    if image_size[0] >= image_size[1]:
        return True
    else:
        return False


def set_file_to_desktop_background(image_file_path):

    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_file_path, 0)


reddit = praw.Reddit(client_id='gSozMpmngIW2Lg',
                     client_secret=os.environ["SECRET"],
                     user_agent='Windows:SubredditBackground:v0.0.0 (by u/shoot2thr1ll284)')

config = configparser.ConfigParser()
config.read("config.ini")
general = config["GENERAL"]
nsfw_allowed = general.getboolean("NSFW_ALLOWED")
subreddits = general["SUBREDDITS"]

# get all urls
urls = get_submissions_for_subreddit(reddit, subreddits, "day", nsfw_allowed)
print(urls)

file_path = ""
found_good = False
while (not found_good) and len(urls) != 0:

    # select specific url at random
    attempt, urls = get_random_url(urls)
    print(attempt)

    # save first attempt at okay file url
    file_path = get_file_from_url(attempt)
    print(file_path)
    if file_path != "":
        found_good = True
        print("good")

# set file to desktop background
if file_path != "":
    set_file_to_desktop_background(file_path)



# https://www.reddit.com/r/learnpython/comments/3vwhvg/changing_wallpaper_on_windows/
# https://stackoverflow.com/questions/3129322/how-do-i-get-monitor-resolution-in-python