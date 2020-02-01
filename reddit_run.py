import os
from dotenv import load_dotenv
from util import base_directory, init_directories
from reddit_api import RedditAPI

env_file_path = os.path.join(base_directory, ".env")
load_dotenv(env_file_path)

if __name__ == "__main__":
    init_directories()

    api = RedditAPI()
    api.do_daily_iteration()
    api.do_weekly_iteration()



