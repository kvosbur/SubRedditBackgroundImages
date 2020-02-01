import praw
import os
from util import readConfigFile, base_directory, get_random_url
from reddit_image import RedditImage
from combine_image import CombineImages

dest_directory = os.path.join(base_directory, "PictureSource")


class RedditAPI:

    apiOjbect = None
    nsfw_allowed = False
    subreddits = ""

    def __init__(self):
        config = readConfigFile()
        general = config["GENERAL"]
        self.nsfw_allowed = general.getboolean("NSFW_ALLOWED")
        self.subreddits = general["SUBREDDITS"]


        self.apiObject = praw.Reddit(client_id='gSozMpmngIW2Lg',
                         client_secret=os.environ["SECRET"],
                         user_agent='Windows:SubredditBackground:v0.0.0 (by u/shoot2thr1ll284)')

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
