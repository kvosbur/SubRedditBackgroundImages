import praw, os
from dotenv import load_dotenv

load_dotenv('.env')

reddit = praw.Reddit(client_id='gSozMpmngIW2Lg',
                     client_secret=os.environ["SECRET"],
                     user_agent='Windows:SubredditBackground:v0.0.0 (by u/shoot2thr1ll284)')

submissions = reddit.subreddit('Animewallpaper').top('day')
print(submissions)

image_urls = []

for sub in submissions:
    print(sub)
    print(sub.title)
    print(sub.permalink)
    print(sub.over_18)
    print(sub.url)
    # parse
    if sub.url != '':
        image_urls.append(sub.url)


print(image_urls)
print(len(image_urls))

print("After")

# https://www.reddit.com/r/learnpython/comments/3vwhvg/changing_wallpaper_on_windows/
# https://stackoverflow.com/questions/3129322/how-do-i-get-monitor-resolution-in-python