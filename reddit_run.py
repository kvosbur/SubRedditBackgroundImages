import os
from dotenv import load_dotenv
from util import base_directory, init_directories
from reddit_api import RedditAPI
import argparse
import signal

env_file_path = os.path.join(base_directory, ".env")
load_dotenv(env_file_path)
apiObject = None

parser = argparse.ArgumentParser(description="Run EDI")
parser.add_argument("--show-progress", action="store_true", help="Show Progress Bars for Downloads")
parser.add_argument("--no-weekly", default=False, action="store_true", help="Disables the program from trying to run the weekly lockscreen photos portion")

def sigterm_handler(signalNum, frame):
    print("\nCleaning Up Files Before Termination\n")
    if apiObject is not None:
        apiObject.do_cleanup()
    exit(0)


if __name__ == "__main__":
    init_directories()
    signal.signal(signal.SIGTERM, sigterm_handler)

    args = parser.parse_args()

    apiObject = RedditAPI(args)
    # apiObject.do_daily_iteration()
    if not args.no_weekly:
        apiObject.do_weekly_iteration()



