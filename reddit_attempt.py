import os
from dotenv import load_dotenv
import datetime
from util import base_directory
from reddit_api import RedditAPI

env_file_path = os.path.join(base_directory, ".env")
load_dotenv(env_file_path)


def save_url_list(url_list):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "PictureSource", "url_list.txt"), "w") as f:
        for url in url_list:
            f.write(url + "\n")


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

    api = RedditAPI()

    api.do_daily_iteration()

    '''
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
    '''

