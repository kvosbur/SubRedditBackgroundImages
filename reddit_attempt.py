import praw, os
from dotenv import load_dotenv
import configparser
import random
import ctypes
import datetime
import shutil
from combine_image import do_combine_landscape_process
from util import base_directory, get_file_from_url

env_file_path = os.path.join(base_directory, ".env")
print(env_file_path)
load_dotenv(env_file_path)

def print_list(l):
    for item in l:
        print(item)

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
        if sub.url != '' and (sub.over_18 == nsfw_allowed):
            image_urls.append((sub.url, sub.permalink))
    return image_urls


def save_url_list(url_list):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "PictureSource", "url_list.txt"), "w") as f:
        for url in url_list:
            f.write(url + "\n")


def get_random_url(url_list):
    url = random.choice(url_list)
    url_list.remove(url)
    return url, url_list


def set_file_to_desktop_background(image_file_path):

    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_file_path, 0)


def should_run_weekly():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PictureSource", "lastran.txt")
    if os.path.exists(file_path):
        # check file to see last time it was run
        with open(file_path, "r") as f:
            time_str = f.readline().replace("\n", "")
            time_obj = datetime.datetime.strptime(time_str, "%Y-%m-%d")
            diff = datetime.datetime.now() - time_obj
            if diff.days >= 7:
                return True

    return False


def set_weekly_run_file():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PictureSource", "lastran.txt")
    with open(file_path, "w") as f:

        time_str = datetime.datetime.now().strftime("%Y-%m-%d")
        f.write(time_str)


def remove_all_background_photos():
    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PictureSource", "LockScreen")
    prev = os.listdir(directory)
    for f in prev:
        full = os.path.join(directory, f)
        os.remove(full)


if __name__ == "__main__":
    reddit = praw.Reddit(client_id='gSozMpmngIW2Lg',
                         client_secret=os.environ["SECRET"],
                         user_agent='Windows:SubredditBackground:v0.0.0 (by u/shoot2thr1ll284)')

    config_file_path = os.path.join(base_directory, "config.ini")
    config = configparser.ConfigParser()
    config.read(config_file_path)
    general = config["GENERAL"]
    nsfw_allowed = general.getboolean("NSFW_ALLOWED")
    subreddits = general["SUBREDDITS"]

    # get all urls
    urls = get_submissions_for_subreddit(reddit, subreddits, "day", nsfw_allowed)
    incorrect_aspect = []
    print(len(urls), "results")

    # get suitable image for desktop background
    file_path = ""
    final_path = ""
    found_good = False
    dest_directory = os.path.join(base_directory, "PictureSource")
    while (not found_good) and len(urls) != 0:

        # select specific url at random
        attempt, urls = get_random_url(urls)
        image_url, post_permalink = attempt
        print(attempt)

        # save first attempt at okay file url
        file_path, final_path, image_size = get_file_from_url(dest_directory, "temp", image_url)
        if file_path != "":
            found_good = True
            with open(os.path.join(dest_directory, "tempStat.txt"), "w") as f:
                f.write(image_url + "\n")
                f.write(post_permalink)
            print("good aspect")
        else:
            temp = list(attempt)
            temp.append(image_size)
            incorrect_aspect.append(temp)

    toBeOrNotToBe = random.randint(0,1)
    # set file to desktop background
    if file_path != "" and toBeOrNotToBe:
        shutil.move(file_path, final_path)
        set_file_to_desktop_background(final_path)
        print_list(incorrect_aspect)
    else:
        # try to combine dailies to create a better bigger image
        do_combine_landscape_process(incorrect_aspect)
        print("Found No Good Aspect Images")



    run_weekly = should_run_weekly()
    dest_directory = os.path.join(base_directory, "PictureSource", "LockScreen")
    iteration = 0
    if run_weekly:
        # remove previous images from folder
        remove_all_background_photos()

        with open(os.path.join(base_directory,"PictureSource", "lockScreenStat.txt"), "w") as f:

            # get suitable images for background
            weekly_list = get_submissions_for_subreddit(reddit, subreddits, "week", nsfw_allowed)
            while len(weekly_list) > 0:
                # select specific url at random
                attempt, urls = get_random_url(weekly_list)
                image_url, post_permalink = attempt

                # get image and save if able
                file_path, final_path, image_size = get_file_from_url(dest_directory, "image" + str(iteration), image_url, check_correct_aspect=False)
                if file_path != "":
                    iteration += 1
                    f.write(file_path + "  |||||  " + post_permalink + "\n")

                print("URLS Left: " + str(len(weekly_list)))

            set_weekly_run_file()

    else:
        print("Weekly not Run")

