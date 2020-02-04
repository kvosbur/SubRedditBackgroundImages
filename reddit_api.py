import praw
import os
from util import readConfigFile, base_directory, get_random_url, remove_all_files
from reddit_image import RedditImage
from combine_image import CombineImages
import datetime
from progress.bar import Bar

dest_directory = os.path.join(base_directory, "PictureSource")
USER_AGENT = 'Windows:SubredditBackground:v0.0.0 (by u/shoot2thr1ll284)'


class RedditAPI:

    apiOjbect = None
    nsfw_allowed = False
    subreddits = ""

    def __init__(self, args):
        self.args = args
        config = readConfigFile()
        general = config["GENERAL"]
        self.nsfw_allowed = general.getboolean("NSFW_ALLOWED")
        self.subreddits = general["SUBREDDITS"]


        self.apiObject = praw.Reddit(client_id='gSozMpmngIW2Lg',
                         client_secret=os.environ["SECRET"],
                         user_agent=USER_AGENT)

    def get_submissions_for_subreddit(self, time_filter="day"):
        submissions = self.apiObject.subreddit(self.subreddits).top(time_filter)
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
            if sub.url != '' and (sub.over_18 == self.nsfw_allowed):
                image_urls.append((sub.url, sub.permalink))
        return image_urls

    def do_daily_iteration(self):
        incorrect_aspect = []
        correct_aspect = []
        try:
            urls = self.get_submissions_for_subreddit("day")

            totalCount = len(urls)
            progressBar = None
            if self.args.show_progress:
                progressBar = Bar("Downloading Daily Images", max=totalCount, suffix='%(index)d / %(max)d  %(percent)d%%')
                progressBar.start()
            # get suitable image for desktop background
            while len(urls) != 0:
                # select specific url at random
                attempt, urls = get_random_url(urls)
                image_url, post_permalink = attempt

                # save first attempt at okay file url
                imageObj = RedditImage(image_url, post_permalink)
                imageObj.get_image_from_url(dest_directory)
                if not imageObj.image_downloaded():
                    continue

                if imageObj.image_is_landscape():
                    correct_aspect.append(imageObj)
                else:
                    incorrect_aspect.append(imageObj)
                if progressBar is not None:
                    progressBar.next()

            if progressBar is not None:
                progressBar.finish()

            if len(incorrect_aspect) > 0:
                ci = CombineImages(incorrect_aspect, dest_directory)
                pathOfResult = ci.do_combine_landscape_process()
                RedditImage.set_image_to_desktop_background(pathOfResult)
            else:
                correct_aspect[0].set_to_desktop_background()

        finally:
            # cleanup all images that had been temporarily downloaded
            for image in incorrect_aspect + correct_aspect:
                image.cleanup()

    @staticmethod
    def should_run_weekly():
        file_path = os.path.join(base_directory, "PictureSource", "lastran.txt")
        if os.path.exists(file_path):
            # check file to see last time it was run
            with open(file_path, "r") as f:
                time_str = f.readline().replace("\n", "")
                time_obj = datetime.datetime.strptime(time_str, "%Y-%m-%d")
                diff = datetime.datetime.now() - time_obj
                if diff.days >= 7:
                    return True
            return False
        else:
            return True

    def set_weekly_run_file(self, destDirectory):
        file_path = os.path.join(destDirectory,"lastran.txt")
        with open(file_path, "w") as f:
            time_str = datetime.datetime.now().strftime("%Y-%m-%d")
            f.write(time_str)

    def do_weekly_iteration(self):
        if RedditAPI.should_run_weekly():
            dest_directory = os.path.join(base_directory, "PictureSource", "LockScreen")
            source_directory = os.path.join(base_directory, "PictureSource")
            remove_all_files(dest_directory)
            weekly_urls = self.get_submissions_for_subreddit("week")
            totalCount = len(weekly_urls)
            progressBar = None
            if self.args.show_progress:
                progressBar = Bar("Downloading Weekly Images", max=totalCount, suffix='%(index)d / %(max)d  %(percent)d%%')
                progressBar.start()

            with open(os.path.join(base_directory, "PictureSource", "lockScreenStat.txt"), "w") as f:
                while len(weekly_urls) > 0:
                    # select specific url at random
                    attempt, urls = get_random_url(weekly_urls)
                    image_url, post_permalink = attempt

                    # get image and save if able
                    imageObj = RedditImage(image_url, post_permalink)
                    imageObj.get_image_from_url(dest_directory)
                    if imageObj.image_downloaded():
                        f.write(str(imageObj) + "\n")

                    if progressBar is not None:
                        progressBar.next()

                if progressBar is not None:
                    progressBar.finish()

            self.set_weekly_run_file(source_directory)
