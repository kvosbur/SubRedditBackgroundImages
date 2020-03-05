import praw
import os
from util import readConfigFile, base_directory, get_random_url, remove_all_files
from reddit_image import RedditImage
from combine_image import CombineImages
import datetime
from progress.bar import Bar
from reddit_logging import log

dest_directory = os.path.join(base_directory, "PictureSource")


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

        self.incorrect_aspect = []
        self.correct_aspect = []


        self.apiObject = praw.Reddit(client_id=os.environ["CLIENT_ID"],
                         client_secret=os.environ["SECRET"],
                         user_agent=os.environ["USER_AGENT"])

    def do_cleanup(self):
        for image in self.incorrect_aspect + self.correct_aspect:
            image.cleanup()

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
            if sub.url != '' and (self.nsfw_allowed or sub.over_18 == self.nsfw_allowed):
                image_urls.append((sub.url, sub.permalink))
        return image_urls

    def do_daily_iteration(self):
        log("Start Daily Iteration", is_heading=True)
        self.incorrect_aspect = []
        self.correct_aspect = []
        progressBar = None
        try:
            urls = self.get_submissions_for_subreddit("day")
            log("URLS Gathered")

            totalCount = len(urls)
            if self.args.show_progress:
                progressBar = Bar("Downloading Daily Images", max=totalCount, suffix='%(index)d / %(max)d  %(percent)d%%')
                progressBar.start()
            # get suitable image for desktop background
            while len(urls) != 0:
                # select specific url at random
                attempt, urls = get_random_url(urls)
                image_url, post_permalink = attempt
                log("Process URL:", image_url, "URLS Left:", len(urls))

                # save first attempt at okay file url
                imageObj = RedditImage(image_url, post_permalink)
                imageObj.get_image_from_url(dest_directory)
                if not imageObj.image_downloaded():
                    continue

                if imageObj.image_is_landscape():
                    self.correct_aspect.append(imageObj)
                else:
                    self.incorrect_aspect.append(imageObj)
                if progressBar is not None:
                    progressBar.next()
                log("URL has been processed")

            if progressBar is not None:
                progressBar.finish()
                progressBar = None

            if len(self.incorrect_aspect) > 0:
                log("Start Image Combining Process")
                ci = CombineImages(self.incorrect_aspect, dest_directory)
                log("Save Resulting Image")
                pathOfResult = ci.do_combine_landscape_process()
                log("Set Image as Desktop Background")
                RedditImage.set_image_to_desktop_background(pathOfResult)
            else:
                self.correct_aspect[0].set_to_desktop_background()
        except KeyboardInterrupt:
            None
        finally:
            # cleanup all images that had been temporarily downloaded
            if progressBar is not None:
                progressBar.finish()
            print("\nCleaning Up Files Before Termination\n")
            self.do_cleanup()


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

    def set_weekly_run_file(self):
        file_path = os.path.join(base_directory, "PictureSource", "lastran.txt")
        with open(file_path, "w") as f:
            time_str = datetime.datetime.now().strftime("%Y-%m-%d")
            f.write(time_str)

    def do_weekly_iteration(self):
        if RedditAPI.should_run_weekly():
            log("Start Weekly Iteration", is_heading=True)
            initialSource = os.path.join(base_directory, "PictureSource", "LockScreenSource")
            finalSource = os.path.join(base_directory, "PictureSource", "LockScreen")
            remove_all_files(initialSource)
            remove_all_files(finalSource)
            weekly_urls = self.get_submissions_for_subreddit("week")
            log("URLS Gathered")
            totalCount = len(weekly_urls)
            progressBar = None
            landscape = []
            portrait = []
            if self.args.show_progress:
                progressBar = Bar("Downloading Weekly Images", max=totalCount, suffix='%(index)d / %(max)d  %(percent)d%%')
                progressBar.start()

            with open(os.path.join(base_directory, "PictureSource", "lockScreenStat.txt"), "w") as f:
                while len(weekly_urls) > 0:
                    # select specific url at random
                    attempt, urls = get_random_url(weekly_urls)
                    image_url, post_permalink = attempt

                    log("Process URL:", image_url, "URLS Left:", len(urls))

                    # get image and save if able
                    imageObj = RedditImage(image_url, post_permalink)
                    imageObj.get_image_from_url(initialSource)
                    if imageObj.image_is_landscape():
                        landscape.append(imageObj)
                    else:
                        portrait.append(imageObj)
                    if imageObj.image_downloaded():
                        f.write(str(imageObj) + "\n")

                    if progressBar is not None:
                        progressBar.next()

                    log("URL has been processed")

                if progressBar is not None:
                    progressBar.finish()

                for imageObj in landscape:
                    imageObj.move_to_folder(finalSource)
                    print("did the copy")

                # iterate through creating landscape photos
                ci = CombineImages(portrait, finalSource)
                ci.iterate_combine_landscape()


            self.set_weekly_run_file()
