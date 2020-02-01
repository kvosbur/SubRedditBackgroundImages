import os
from dotenv import load_dotenv
from util import base_directory, init_directories
from reddit_api import RedditAPI
import argparse

env_file_path = os.path.join(base_directory, ".env")
load_dotenv(env_file_path)

parser = argparse.ArgumentParser(description="Run EDI")
parser.add_argument("--show-progress", action="store_true", help="Show Progress Bars for Downloads")


if __name__ == "__main__":
    init_directories()

    args = parser.parse_args()

    api = RedditAPI(args)
    api.do_daily_iteration()
    api.do_weekly_iteration()



